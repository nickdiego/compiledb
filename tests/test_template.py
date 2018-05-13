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
from compiledb.parser import parse

def test_empty():
    build_log = ''
    proj_dir = '/tmp'
    incpath_prefix = proj_dir
    exclude_list = []
    verbose = False

    (count, skipped, db) = parse(build_log, proj_dir, incpath_prefix, exclude_list, verbose)
    assert count == 0
    assert skipped == 0
    assert db is not None
    assert type(db) == list
    assert len(db) == 0

