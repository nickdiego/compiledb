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
# ex: ts=2 sw=4 et filetype=python

import argparse
import json
import os
import sys

from compiledb.parser import parse_build_log, Error
from compiledb.utils import msg, input_file, output_file


def generate_json_compdb(input_path, output_path, proj_dir=os.getcwd(),
                         verbose=False, force=False, include_prefix=None,
                         exclude_list=[], pretty_output=True):

    if not os.path.isdir(proj_dir):
        raise Error("Project dir '{}' does not exists!".format(proj_dir))

    with input_file(input_path) as build_log:
        msg("## Processing build commands from '{}'".format(
            'std input' if input_path is None else input_path))
        result = parse_build_log(build_log, proj_dir, include_prefix,
                                 exclude_list, verbose)

        output_str = 'std output' if output_path is None else output_path
        msg("## Writing compilation database with {} entries to {}".format(
            len(result.compdb), output_str))

        with output_file(output_path) as output:
            json.dump(result.compdb, output, indent=pretty_output)
            output.write(os.linesep)

        msg("## Done.")


def cli():
    if(sys.platform.startswith("win32")):
        msg("Error: Windows is not supported")

    desc = "Process build log/commands and generates compilation database for it."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-v", "--verbose", default=False, action="store_true",
                        help="Show output from build process")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Overwrite the file if it exists.")
    parser.add_argument("-o", "--output", dest='output_path', help="Save the config " +
                        "file as OUTPUT. Default: std output")
    parser.add_argument("-i", "--input", dest='input_path', help="File path to be " +
                        "used as input. It must contain the make output. Default: stdin.")
    parser.add_argument("-p", "--include-prefix", help="Prefix path to be " +
                        "concatenated to each include path flag. Default: $PWD")
    parser.add_argument("-e", "--exclude", default=[], nargs='+', dest='exclude_list',
                        help="Space-separated list of regular expressions to exclude files.")
    parser.add_argument('proj_dir', metavar='PROJ_DIR', nargs='?', default=os.getcwd(),
                        help="The root directory of the project. Default: $PWD")

    args = vars(parser.parse_args())

    try:
        generate_json_compdb(**args)
        sys.exit(0)
    except Error as e:
        msg(str(e))
        sys.exit(1)

