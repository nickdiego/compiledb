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
# ex: ts=2 sw=4 et filetype=python

import json
import os
import sys
import logging

from compiledb.parser import parse_build_log, Error


logger = logging.getLogger(__name__)


def __is_stdout(pfile):
    try:
        return pfile.name == sys.stdout.name or isinstance(pfile.name, int)
    except AttributeError:
        return pfile == sys.stdout


def basename(stream):
    if __is_stdout(stream):
        return "<stdout>"
    else:
        return os.path.basename(stream.name)


def generate_json_compdb(instream=None, proj_dir=os.getcwd(), exclude_files=[], add_predefined_macros=False,
                         use_full_path=False, command_style=False):
    if not os.path.isdir(proj_dir):
        raise Error("Project dir '{}' does not exists!".format(proj_dir))

    logger.info("## Processing build commands from {}".format(basename(instream)))
    result = parse_build_log(instream, proj_dir, exclude_files, add_predefined_macros=add_predefined_macros,
                             use_full_path=use_full_path, command_style=command_style)
    return result


def write_json_compdb(compdb, outstream, force=False, pretty_output=True):
    logger.info("## Writing compilation database with {} entries to {}".format(
        len(compdb), basename(outstream)))

    # We could truncate after reading, but here is easier to understand
    if not __is_stdout(outstream):
        outstream.seek(0)
        outstream.truncate()
    json.dump(compdb, outstream, indent=pretty_output)
    outstream.write(os.linesep)


def load_json_compdb(outstream):
    try:
        if __is_stdout(outstream):
            return []

        # Read from beggining of file
        outstream.seek(0)
        compdb = json.load(outstream)
        logger.info("## Loaded compilation database with {} entries from {}".format(
            len(compdb), basename(outstream)))
        return compdb
    except Exception as e:
        logger.debug("## Failed to read previous {}: {}".format(basename(outstream), e))
        return []


def merge_compdb(compdb, new_compdb, check_files=True):
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


def generate(infile, outfile, build_dir, exclude_files, overwrite=False, strict=False,
             add_predefined_macros=False, use_full_path=False, command_style=False):
    try:
        r = generate_json_compdb(infile, proj_dir=build_dir, exclude_files=exclude_files,
                                 add_predefined_macros=add_predefined_macros, use_full_path=use_full_path,
                                 command_style=command_style)
        compdb = [] if overwrite else load_json_compdb(outfile)
        compdb = merge_compdb(compdb, r.compdb, strict)
        write_json_compdb(compdb, outfile)
        logger.info("## Done.")
        return True
    except Error as e:
        logger.error(e)
        return False
