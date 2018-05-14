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
import argparse
import json
import os
import os.path
import sys

from compiledb.parser import parse as parse_build_log
from compiledb.utils import msg, input_file, output_file


def generate(args):
    if(sys.platform.startswith("win32")):
        msg("Error: Windows is not supported")

    # parse command-line args
    parser = argparse.ArgumentParser(description="Process build output and automatically generates compilation database file for it.")
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help="Show output from build process")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite the file if it exists.")
    parser.add_argument("-o", "--output", help="Save the config file as OUTPUT. Default: compile_commands.json")
    parser.add_argument("-i", "--input", help="File path to be used as input. It must contain the make output. Default: stdin.")
    parser.add_argument("-p", "--include-prefix", help="Prefix path to be concatenated to each include path flag. Default: $PWD")
    parser.add_argument("-e", "--exclude", default=[], nargs='+', help="Space-separated list of regular expressions to exclude files.")
    parser.add_argument("PROJ_DIR", nargs='?', default=os.getcwd(), help="The root directory of the project.")
    args = vars(parser.parse_args(args))

    include_path_prefix = args["include_prefix"]
    output_path = args["output"]
    input_path = args["input"]
    exclude_list = args["exclude"]
    verbose = args["verbose"]
    pretty_output = True

    proj_dir = os.path.abspath(args["PROJ_DIR"])
    if not os.path.isdir(proj_dir):
        msg("Error: Project dir '{}' does not exists!".format(proj_dir))
        return 1

    with input_file(input_path) as build_log:
        msg("## Processing build commands from '{}'".format('std input' if input_path is None else input_path))
        (count, skipped, compile_db) = parse_build_log(build_log, proj_dir, include_path_prefix, exclude_list, verbose)
        output_str = 'std output' if output_path is None else output_path
        msg("## Writing compilation database with {} entries to {}".format(len(compile_db), output_str))
        generate_compile_db_file(compile_db, output_path, pretty_output)
        msg("## Done.")

    return 0


def generate_compile_db_file(compile_db, output_path, indent=False):
    with output_file(output_path) as output:
        json.dump(compile_db, output, indent=indent)
        output.write(os.linesep)

# ex: ts=2 sw=4 et filetype=python

