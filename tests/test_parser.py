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
from os import path, getcwd

from compiledb.parser import parse_build_log

data_dir = path.abspath(path.join(path.dirname(__file__), 'data'))


def test_empty():
    build_log = ''
    proj_dir = '/tmp'
    incpath_prefix = proj_dir
    exclude_list = []
    verbose = False

    result = parse_build_log(build_log, proj_dir, incpath_prefix, exclude_list,
                             verbose)
    assert result.count == 0
    assert result.skipped == 0
    assert result.compdb is not None
    assert type(result.compdb) == list
    assert len(result.compdb) == 0


def test_trivial_build_command():
    pwd = getcwd()
    build_log = ['gcc -o hello.o -c hello.c']
    result = parse_build_log(
        build_log,
        proj_dir=pwd,
        inc_prefix=None,
        exclude_list=[],
        verbose=False)

    assert result.count == 1
    assert result.skipped == 0
    assert len(result.compdb) == 1
    assert result.compdb[0] == {
        'directory': pwd,
        'file': 'hello.c',
        'arguments': [
            'cc', '-c', 'hello.c'
        ]
    }


def test_automake_command():
    pwd = getcwd()
    with input_file('autotools_simple') as build_log:
        result = parse_build_log(
            build_log,
            proj_dir=pwd,
            inc_prefix=None,
            exclude_list=[],
            verbose=False)

    assert result.count == 1
    assert result.skipped == 0
    assert len(result.compdb) == 1
    assert result.compdb[0] == {
        'directory': pwd,
        'file': './main.c',
        'arguments': [
            'cc',
            '-DPACKAGE_NAME="hello"',
            '-DPACKAGE_VERSION="1.0.0"',
            '-DSTDC_HEADERS=1',
            '-I.',
            '-I../../src/libhello',
            '-c',
            './main.c'
        ]
    }


def input_file(relpath):
    relpath = '{}.txt'.format(relpath)
    return open(path.join(data_dir, relpath), 'r')

