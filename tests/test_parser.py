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
    exclude_files = []
    verbose = False

    result = parse_build_log(build_log, proj_dir, exclude_files, verbose)
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
        exclude_files=[],
        verbose=False)

    assert result.count == 1
    assert result.skipped == 0
    assert len(result.compdb) == 1
    assert result.compdb[0] == {
        'directory': pwd,
        'file': 'hello.c',
        'command': 'gcc -o hello.o -c hello.c'
    }


def test_build_commands_with_wrapper():
    pwd = getcwd()
    build_log = [
        'ccache gcc -o hello.o -c hello.c\n'
        'icecc clang++ -c somefile.cpp\n'
        'icecc ccache arm1999-gnu-etc-g++ -c main.cpp -o main.o\n'
        'unknown-wrapper g++ -c main.cpp -o main.o\n'
    ]
    result = parse_build_log(
        build_log,
        proj_dir=pwd,
        exclude_files=[],
        verbose=True)

    assert result.count == 4
    assert result.skipped == 0
    assert len(result.compdb) == 4
    assert result.compdb == [{
        'directory': pwd,
        'file': 'hello.c',
        'command': 'gcc -o hello.o -c hello.c'
    }, {
        'directory': pwd,
        'file': 'somefile.cpp',
        'command': 'clang++ -c somefile.cpp'
    }, {
        'directory': pwd,
        'file': 'main.cpp',
        'command': 'arm1999-gnu-etc-g++ -c main.cpp -o main.o'
    }, {
        'directory': pwd,
        'file': 'main.cpp',
        'command': 'g++ -c main.cpp -o main.o'
    }]


def test_parse_with_non_build_cmd_entries():
    pwd = getcwd()
    build_log = [
        'random build log message..\n',
        'gcc -c valid.c\n',
        'some other random build log message with g++ or gcc included.\n',
        '\n',
        '',
        'g++ -c valid2.cc\n',
    ]
    # These ones will reach the bashlex parsing code and
    # would generate a parsing exception
    # https://github.com/nickdiego/compiledb-generator/issues/38
    build_log += [
        'checking for gcc... (cached) gcc\n',
        'checking whether gcc accepts -g... (cached) yes\n'
    ]
    result = parse_build_log(
        build_log,
        proj_dir=pwd,
        exclude_files=[],
        verbose=True)

    assert result.count == 2
    assert result.skipped == 6
    assert len(result.compdb) == 2
    assert result.compdb == [{
        'directory': pwd,
        'file': 'valid.c',
        'command': 'gcc -c valid.c',
    }, {
        'directory': pwd,
        'file': 'valid2.cc',
        'command': 'g++ -c valid2.cc'
    }]


def test_automake_command():
    pwd = getcwd()
    with input_file('autotools_simple') as build_log:
        result = parse_build_log(
            build_log,
            proj_dir=pwd,
            exclude_files=[],
            verbose=False)

    assert result.count == 1
    assert result.skipped == 0
    assert len(result.compdb) == 1
    assert result.compdb[0] == {
        'directory': pwd,
        'file': './main.c',
        'command': ' '.join([
            'gcc',
            '-DPACKAGE_NAME="hello"',
            '-DPACKAGE_VERSION="1.0.0"',
            '-DSTDC_HEADERS=1',
            '-I.',
            '-I../../src/libhello',
            '-c',
            '-o', 'hello_world1-main.o',
            './main.c'
        ])
    }


def test_multiple_commands_per_line():
    pwd = getcwd()
    with input_file('multiple_commands_oneline') as build_log:
        result = parse_build_log(
            build_log,
            proj_dir=pwd,
            exclude_files=[],
            verbose=False)

    assert result.count == 2
    assert result.skipped == 0
    assert len(result.compdb) == 2
    assert result.compdb[0] == {
        'directory': pwd,
        'file': './path/src/hein.cpp',
        'command': ' '.join([
            'g++',
            '-c', './path/src/hein.cpp',
            '-o', 'out.o'
        ])
    }


def input_file(relpath):
    relpath = '{}.txt'.format(relpath)
    return open(path.join(data_dir, relpath), 'r')

