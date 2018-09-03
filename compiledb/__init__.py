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


def generate_json_compdb(instream=None, proj_dir=os.getcwd(), verbose=False, exclude_files=[]):
    if not os.path.isdir(proj_dir):
        raise Error("Project dir '{}' does not exists!".format(proj_dir))

    print("## Processing build commands from {}".format(instream.name))
    result = parse_build_log(instream, proj_dir, exclude_files, verbose)
    return result


def write_json_compdb(compdb, outstream=None, verbose=False,
                      force=False, pretty_output=True):
    print("## Writing compilation database with {} entries to {}".format(
        len(compdb), outstream.name))

    json.dump(compdb, outstream, indent=pretty_output)
    outstream.write(os.linesep)


def load_json_compdb(verbose=False):
    compdb_path = 'compile_commands.json'
    try:
        with open(compdb_path, "r") as instream:
            compdb = json.load(instream)
            print("## Loaded compilation database with {} entries from {}".format(
                len(compdb), compdb_path))
            return compdb
    except Exception as e:
        if verbose:
            print("## Failed to read previous {}: {}".format(compdb_path, e))
        return []


def merge_compdb(compdb, new_compdb, check_files=True, verbose=False):
    def gen_key(entry):
        if 'directory' in entry:
            return os.path.join(entry['directory'], entry['file'])
        return entry['directory']

    def check_file(path):
        return True if not check_files else os.path.exists(path)

    orig = {gen_key(c): c for c in compdb if 'file' in c}
    new = {gen_key(c): c for c in new_compdb if 'file' in c}
    orig.update(new)
    return [v for k, v in orig.items() if check_file(k)]


def generate(infile, outfile, build_dir, exclude_files, verbose, overwrite=False, strict=False):
    try:
        r = generate_json_compdb(infile, proj_dir=build_dir, verbose=verbose, exclude_files=exclude_files)
        compdb = [] if overwrite else load_json_compdb(verbose)
        compdb = merge_compdb(compdb, r.compdb, strict, verbose)
        write_json_compdb(compdb, outfile, verbose=verbose)
        print("## Done.")
        return True
    except Error as e:
        print(str(e))
        return False
