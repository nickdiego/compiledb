#!/usr/bin/env python
#
#   compiledb-generator: Tool for generating LLVM Compilation Database
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
import bashlex.parser
import bashlex.ast
import re
import subprocess
from sys import version_info


# Internal variables used to parse build log entries
# TODO: Most of them will be removed soon in favor of an
# bashlex/argparse based parsing (mainly for command line options
# in to avoid reinventing the wheel and eliminate false positives
# for compiler, wrappers and their flags
cc_compile_regex = re.compile(".*-?g?cc|.*-?clang")
cpp_compile_regex = re.compile(".*-?[gc]\+\+|.*-?clang\+\+")
file_regex = re.compile("(^.+\.c$)|(^.+\.cc$)|(^.+\.cpp$)|(^.+\.cxx$)")

# Leverage make --print-directory option
make_enter_dir = re.compile("^\s*make\[\d+\]: Entering directory [`\'\"](?P<dir>.*)[`\'\"]\s*$")
make_leave_dir = re.compile("^\s*make\[\d+\]: Leaving directory .*$")


class ParsingResult(object):
    def __init__(self):
        self.skipped = 0
        self.count = 0
        self.compdb = []

    def __str__(self):
        return "Line count: {}, Skipped: {}, Entries: {}".format(
            self.count, self.skipped, str(self.compdb))


class Error(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "Error: {}".format(self.msg)


def parse_build_log(build_log, proj_dir, inc_prefix, exclude_list, verbose):
    result = ParsingResult()

    def skip_line(cmd, reason):
        if verbose:
            print("[INFO] Line {}: {}. Ignoring: '{}'".format(lineno, reason, cmd))
        result.skipped += 1

    exclude_regex = None
    if len(exclude_list) > 0:
        try:
            exclude_regex = re.compile("|".join(exclude_list))
        except:
            raise Error('Regular expression not valid: {}'.format(exclude_list))

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

        commands = []
        try:
            commands = CommandProcessor.process(line, working_dir)
        except (bashlex.errors.ParsingError, subprocess.CalledProcessError) as err:
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

            if filepath and exclude_regex and exclude_regex.match(filepath):
                skip_line(cmd, "Excluding file (regex='{}')".format('|'.join(exclude_list)))
                continue

            # add entry to database
            if (verbose):
                print("cmd={} --> {}".format(len(result.compdb), filepath))

            result.compdb.append({
                'directory': working_dir,
                'command': unescape(cmd),
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

    def do_process(self, tree):
        self.visit(tree)
        self.check_last_cmd()
        return self.commands

    def visitcommand(self, node, cmd):
        self.check_last_cmd()
        self.cmd = self.line[node.pos[0]:node.pos[1]]
        # print('New command: {}'.format(self.cmd))
        return True

    def visitword(self, node, word):
        # Check if it looks like an entry of interest and
        # and try to determine the compiler
        if self.compiler is None:
            if cc_compile_regex.match(word) or cpp_compile_regex.match(word):
                self.compiler = word
        elif (file_regex.match(word)):
            self.filepath = word
        return True

    def check_last_cmd(self):
        # check if it seems to be a compilation command
        if self.compiler is not None:
            self.commands.append(dict(compiler=self.compiler, filepath=self.filepath, cmd=self.cmd))
            res = True
        # reset state to process new command
        self.reset()


def unescape(s):
    return s.encode().decode('unicode_escape')


if version_info[0] >= 3:  # Python 3
    def run_cmd(cmd, encoding='utf-8', **kwargs):
        return subprocess.check_output(cmd, encoding=encoding, **kwargs)
else:  # Python 2
    def run_cmd(cmd, encoding='utf-8', **kwargs):
        return subprocess.check_output(cmd, **kwargs)

# ex: ts=2 sw=4 et filetype=python
