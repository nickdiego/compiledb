#!/usr/bin/env python2
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
import os.path
import re

from compiledb.utils import msg

class ParsingResult(object):
    def __init__(self):
        self.skipped = 0
        self.count = 0
        self.compdb = []

    def __str__(self):
        return "Line count: {}, Skipped: {}, Entries: {}".format(
                self.count, self.skipped, len(self.compdb))


def parse_build_log(build_log, proj_dir, inc_prefix, exclude_list, verbose):
    result = ParsingResult()

    cc_compile_regex = re.compile("(.*-?g?cc )|(.*-?clang )")
    cpp_compile_regex = re.compile("(.*-?[gc]\+\+ )|(.*-?clang\+\+ )")

    # Leverage make --print-directory option
    make_enter_dir = re.compile("^\s*make\[\d+\]: Entering directory [`\'\"](?P<dir>.*)[`\'\"]\s*$")
    make_leave_dir = re.compile("^\s*make\[\d+\]: Leaving directory .*$")

    # Flags we want:
    # -includes (-i, -I)
    # -warnings (-Werror), but no assembler, etc. flags (-Wa,-option)
    # -language (-std=gnu99) and standard library (-nostdlib)
    # -defines (-D)
    # -m32 -m64
    flags_whitelist = [
        "-c",
        "-m.+",
        "-W[^,]*",
        "-[iIDF].*",
        "-std=[a-z0-9+]+",
        "-(no)?std(lib|inc)",
        "-D([a-zA-Z0-9_]+)=?(.*)",
        "--sysroot=?.*"
    ]
    flags_whitelist = re.compile("|".join(map("^{}$".format, flags_whitelist)))

    # Used to only bundle filenames with applicable arguments
    filename_flags = ["-o", "-I", "-isystem", "-iquote", "-include", "-imacros", "-isysroot", "--sysroot"]
    invalid_include_regex = re.compile("(^.*out/.+_intermediates.*$)|(.+/proguard.flags$)")

    exclude_regex = None
    if len(exclude_list) > 0:
        try:
            exclude_regex = re.compile("|".join(exclude_list))
        except:
            msg('Error: Regular expression not valid: {}'.format(regex_pattern))
            return None

    file_regex = re.compile("(^.+\.c$)|(^.+\.cc$)|(^.+\.cpp$)|(^.+\.cxx$)")

    compiler = None
    dir_stack = [proj_dir]
    working_dir = proj_dir

    # Process build log
    for line in build_log:
        # Concatenate line if need
        accumulate_line = line
        while (line.endswith('\\\n')):
            accumulate_line = accumulate_line[:-2]
            line = next(build_log, '')
            accumulate_line += line
        line = accumulate_line

        # Parse directory that make entering/leaving
        enter_dir = make_enter_dir.match(line)
        if (make_enter_dir.match(line)):
            working_dir = enter_dir.group('dir')
            dir_stack.append(working_dir)
        elif (make_leave_dir.match(line)):
            dir_stack.pop()
            working_dir = dir_stack[-1]

        if (cc_compile_regex.match(line)):
            compiler = 'cc'
        elif (cpp_compile_regex.match(line)):
            compiler = 'c++'
        else:
            continue

        arguments = [compiler]
        words = split_cmd_line(line)[1:]
        filepath = None
        result.count += 1

        for (i, word) in enumerate(words):
            if (file_regex.match(word)):
                filepath = word

            if(word[0] != '-' or not flags_whitelist.match(word)):
                continue

            word = word.decode('unicode_escape')

            # include arguments for this option, if there are any, as a tuple
            if(i != len(words) - 1 and word in filename_flags and words[i + 1][0] != '-'):
                w = words[i + 1]
                p = w if inc_prefix is None else os.path.join(inc_prefix, w)
                if not invalid_include_regex.match(p):
                    arguments.extend([word, p])
            else:
                if word.startswith("-I"):
                    opt = word[0:2]
                    val = word[2:]
                    p = val if inc_prefix is None else os.path.join(inc_prefix, val)
                    if not invalid_include_regex.match(p):
                        arguments.append(opt + p)
                else:
                    arguments.append(word)

        if filepath and exclude_regex and exclude_regex.match(filepath):
            if verbose:
                msg('excluding file {}'.format(filepath))
            filepath = None

        if filepath is None:
            # msg("Empty file name. Ignoring: {}".format(line))
            result.skipped += 1
            continue

        # add entry to database
        # TODO performance: serialize to json file here?
        if (verbose):
            msg("args={} --> {}".format(len(arguments), filepath))

        arguments.append(filepath)
        result.compdb.append({
            'directory': working_dir,
            'file': filepath,
            'arguments': arguments
        })

    return result


def split_cmd_line(line):
    # Pass 1: split line using whitespace
    words = line.strip().split()
    # Pass 2: merge words so that the no. of quotes is balanced
    res = []
    for w in words:
        if(len(res) > 0 and unbalanced_quotes(res[-1])):
            res[-1] += " " + w
        else:
            res.append(w)
    return res


def unbalanced_quotes(s):
    single = 0
    double = 0
    for c in s:
        if(c == "'"):
            single += 1
        elif(c == '"'):
            double += 1
    return (single % 2 == 1 or double % 2 == 1)


# ex: ts=2 sw=4 et filetype=python
