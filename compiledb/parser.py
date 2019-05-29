#!/usr/bin/env python
#
#   compiledb: Tool for generating LLVM Compilation Database
#   files for make-based build systems.
#
#   Copyright (c) 2017 Nick Diego Yamane <nick.diego@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import bashlex
import re
import logging

from compiledb.compiler import get_compiler
from compiledb.utils import run_cmd

# Internal variables used to parse build log entries
cc_compile_regex = re.compile(r"^.*-?g?cc-?[0-9.]*$|^.*-?clang-?[0-9.]*$")
cpp_compile_regex = re.compile(r"^.*-?[gc]\+\+-?[0-9.]*$|^.*-?clang\+\+-?[0-9.]*$")
file_regex = re.compile(r"^.+\.c$|^.+\.cc$|^.+\.cpp$|^.+\.cxx$|^.+\.s$", re.IGNORECASE)
compiler_wrappers = {"ccache", "icecc", "sccache"}

# Leverage `make --print-directory` option
make_enter_dir = re.compile(r"^\s*make\[\d+\]: Entering directory [`\'\"](?P<dir>.*)[`\'\"]\s*$")
make_leave_dir = re.compile(r"^\s*make\[\d+\]: Leaving directory .*$")

# We want to skip such lines from configure to avoid spurious MAKE expansion errors.
checking_make = re.compile(r"^checking whether .* sets \$\(\w+\)\.\.\. (yes|no)$")

logger = logging.getLogger(__name__)


class ParsingResult(object):
    def __init__(self):
        self.skipped = 0
        self.count = 0
        self.compdb = []

    def __str__(self):
        return "Line count: {}, Skipped: {}, Entries: {}".format(self.count, self.skipped, str(self.compdb))


class Error(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "Error: {}".format(self.msg)


def parse_build_log(build_log, proj_dir, exclude_files, command_style=False, add_predefined_macros=False,
                    use_full_path=False, extra_wrappers=[]):
    result = ParsingResult()

    def skip_line(cmd, reason):
        logger.debug("Line {}: {}. Ignoring: '{}'".format(lineno, reason, cmd))
        result.skipped += 1

    exclude_files_regex = None
    if len(exclude_files) > 0:
        try:
            exclude_files = "|".join(exclude_files)
            exclude_files_regex = re.compile(exclude_files)
        except re.error:
            raise Error('Exclude files regex not valid: {}'.format(exclude_files))

    compiler_wrappers.update(extra_wrappers)

    dir_stack = [proj_dir]
    working_dir = proj_dir
    lineno = 0

    # Process build log
    for line in build_log:
        lineno += 1
        # Concatenate line if need
        accumulate_line = line
        while (line.endswith('\\\n')):
            accumulate_line = accumulate_line[:-2]
            line = next(build_log, '')
            accumulate_line += line
        line = accumulate_line.rstrip()

        # Parse directory that make entering/leaving
        enter_dir = make_enter_dir.match(line)
        if (make_enter_dir.match(line)):
            working_dir = enter_dir.group('dir')
            dir_stack.append(working_dir)
            continue
        if (make_leave_dir.match(line)):
            dir_stack.pop()
            working_dir = dir_stack[-1]
            continue
        if (checking_make.match(line)):
            continue

        commands = []
        try:
            commands = CommandProcessor.process(line, working_dir)
        except Exception as err:
            msg = 'Failed to parse build command [Details: ({}) {}]'.format(type(err), str(err))
            skip_line(line, msg)
            continue

        if not commands:
            result.skipped += 1

        for c in commands:
            filepath = c['filepath']
            cmd = c['cmd']
            if filepath is None:
                skip_line(cmd, 'Empty file name')
                continue
            else:
                result.count += 1

            if filepath and exclude_files_regex and exclude_files_regex.match(filepath):
                skip_line(cmd, "Excluding file (regex='{}')".format(exclude_files))
                continue

            wrappers = c['wrappers']
            unknown = ["'%s'" % w for w in wrappers if w not in compiler_wrappers]
            if unknown:
                unknown = ', '.join(unknown)
                logger.debug("Add command with unknown wrapper(s) {}".format(unknown))

            # add entry to database
            tokens = c['tokens']
            arguments = [unescape(a) for a in tokens[len(wrappers):]]

            compiler = get_compiler(arguments[0])

            if add_predefined_macros:
                predefined_macros = compiler.get_predefined_macros(arguments, filepath)
                arguments.extend(predefined_macros)

            if use_full_path:
                arguments[0] = compiler.full_path

            command_str = ' '.join(arguments)

            logger.debug("Adding command {}: {}".format(len(result.compdb), command_str))

            if command_style:
                result.compdb.append({
                    'directory': working_dir,
                    'command': command_str,
                    'file': filepath,
                })
            else:
                result.compdb.append({
                    'directory': working_dir,
                    'arguments': arguments,
                    'file': filepath,
                })

    return result


class SubstCommandVisitor(bashlex.ast.nodevisitor):
    """Uses bashlex to parse and process sh/bash substitution commands.
       May result in a parsing exception for invalid commands."""
    def __init__(self):
        self.substs = []

    def visitcommandsubstitution(self, n, cmd):
        self.substs.append(n)
        return False


class CommandProcessor(bashlex.ast.nodevisitor):
    """Uses bashlex to parse and traverse the resulting bash AST
       looking for and extracting compilation commands."""
    @staticmethod
    def process(line, wd):
        trees = bashlex.parser.parse(line)
        if not trees:
            return []
        for tree in trees:
            svisitor = SubstCommandVisitor()
            svisitor.visit(tree)
            substs = svisitor.substs
            substs.reverse()
            preprocessed = list(line)
            for s in substs:
                start, end = s.command.pos
                s_cmd = line[start:end]
                out = run_cmd(s_cmd, shell=True, cwd=wd)
                start, end = s.pos
                preprocessed[start:end] = out.strip()
            preprocessed = ''.join(preprocessed)

        trees = bashlex.parser.parse(preprocessed)
        processor = CommandProcessor(preprocessed, wd)
        for tree in trees:
            processor.do_process(tree)
        return processor.commands

    def __init__(self, line, wd):
        self.line = line
        self.wd = wd
        self.commands = []
        self.reset()

    def reset(self):
        self.compiler = None
        self.cmd = None
        self.filepath = None
        self.tokens = []
        self.wrappers = []

    def do_process(self, tree):
        self.visit(tree)
        self.check_last_cmd()
        return self.commands

    def visitcommand(self, node, cmd):
        self.check_last_cmd()
        self.cmd = self.line[node.pos[0]:node.pos[1]]
        logger.debug('New command: {}'.format(self.cmd))
        return True

    def visitword(self, node, word):
        # Check if it looks like an entry of interest and
        # and try to determine the compiler
        if self.compiler is None:
            if ((cc_compile_regex.match(word) or cpp_compile_regex.match(word)) and
                    word not in compiler_wrappers):
                self.compiler = word
            else:
                self.wrappers.append(word)
        elif (file_regex.match(word)):
            self.filepath = word

        self.tokens.append(word)
        return True

    def check_last_cmd(self):
        # check if it seems to be a compilation command
        if self.compiler is not None:
            self.commands.append(dict(cmd=self.cmd, wrappers=self.wrappers, tokens=self.tokens,
                                 compiler=self.compiler, filepath=self.filepath))
        # reset state to process new command
        self.reset()


def unescape(s):
    return s.encode().decode('unicode_escape')

# ex: ts=2 sw=4 et filetype=python
