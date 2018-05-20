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

import json
import os
import sys

from compiledb.parser import parse_build_log, Error


def generate_json_compdb(instream=None, proj_dir=os.getcwd(), verbose=False,
                         include_prefix=None, exclude_list=[]):
    if not os.path.isdir(proj_dir):
        raise Error("Project dir '{}' does not exists!".format(proj_dir))

    print("## Processing build commands from {}".format(instream.name))
    result = parse_build_log(instream, proj_dir, include_prefix,
                             exclude_list, verbose)
    return result


def write_json_compdb(compdb, outstream=None, verbose=False,
                      force=False, pretty_output=True):
    print("## Writing compilation database with {} entries to {}".format(
        len(compdb), outstream.name))

    json.dump(compdb, outstream, indent=pretty_output)
    outstream.write(os.linesep)


def generate(infile, outfile, build_dir, inc_prefix, exclude_list, verbose, **kwargs):
    try:
        r = generate_json_compdb(infile, proj_dir=build_dir, verbose=verbose,
                                 include_prefix=inc_prefix, exclude_list=exclude_list)
        write_json_compdb(r.compdb, outfile, verbose=verbose)
        print("## Done.")
        sys.exit(0)
    except Error as e:
        print(str(e))
        sys.exit(1)
