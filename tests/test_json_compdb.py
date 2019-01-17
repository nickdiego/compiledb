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
import os
import json
import click
import pytest
from compiledb import load_json_compdb, generate
from tests.common import input_file, data_dir


multiple_commands_oneline_compdb = [
    {
        'directory': os.getcwd(),
        'file': './path/src/hein.cpp',
        'arguments': [
            'g++',
            '-c', './path/src/hein.cpp',
            '-o', 'out.o'
        ]
    },
    {
        'directory': os.getcwd(),
        'file': 'main.c',
        'arguments': [
            'gcc',
            '-c',
            '-o', 'main.o',
            'main.c'
        ]
    }
]


def test_load_no_compdb_path_default_file_not_exist(capsys):
    assert load_json_compdb() == []
    assert capsys.readouterr().out == ''


def test_load_no_compdb_path_verbose_default_file_not_exist(capsys):
    assert load_json_compdb(verbose=True) == []
    assert 'Failed to read previous compile_commands.json' in capsys.readouterr().out


def test_load_no_compdb_path_default_file_exists(capsys):
    try:
        orig_pwd = os.getcwd()
        os.chdir(data_dir)
        expected_compdb = [
            {
                'file': 'foo.cpp',
                'directory': 'data',
                'arguments': [
                    'g++',
                    'foo.cpp',
                    '-o',
                    'foo.o'
                ]
            }
        ]
        assert load_json_compdb() == expected_compdb
        assert (
            'Loaded compilation database with 1 entries from compile_commands.json'
            in capsys.readouterr().out
        )
    finally:
        os.chdir(orig_pwd)


def test_load_compdb_path_verbose_file_not_exist(capsys):
    compdb_path = os.path.join(data_dir, 'nonexistent.json')
    assert load_json_compdb('nonexistent.json', True) == []
    assert 'Failed to read previous nonexistent.json' in capsys.readouterr().out


def test_load_compdb_path_file_exists(capsys):
    compdb_path = os.path.join(data_dir, 'compile_commands2.json')
    expected_compdb = [
        {
            'file': 'bar.cpp',
            'directory': 'data',
            'arguments': [
                'g++',
                'bar.cpp',
                '-o',
                'bar.o'
            ]
        }
    ]
    assert load_json_compdb(compdb_path) == expected_compdb
    assert (
        'Loaded compilation database with 1 entries from ' + compdb_path
        in capsys.readouterr().out
    )


@pytest.mark.parametrize('filename', ['compile_commands.json', 'nonexistent.json'])
def test_generate_input_file_not_exist(capsys, filename):
    pwd = os.getcwd()
    with input_file('multiple_commands_oneline') as logstream, \
            click.utils.LazyFile(filename, 'w') as outstream:
        assert generate(
            logfile=logstream,
            infile=filename,
            outfile=outstream,
            build_dir=pwd,
            exclude_files=[],
            verbose=True,
            overwrite=False,
            strict=False
        )

    assert_compdb_equals(filename, multiple_commands_oneline_compdb)
    output = capsys.readouterr().out
    assert 'Failed to read previous ' + filename in output
    assert 'Writing compilation database with 2 entries to ' + filename in output


def test_generate_input_file_exists(capsys):
    pwd = os.getcwd()
    filename = os.path.join(data_dir, 'compile_commands2.json')
    compdb_path = 'compile_commands.json'
    with input_file('multiple_commands_oneline') as logstream, \
            click.utils.LazyFile(compdb_path, 'w') as outstream:
        assert generate(
            logfile=logstream,
            infile=filename,
            outfile=outstream,
            build_dir=pwd,
            exclude_files=[],
            verbose=False,
            overwrite=False,
            strict=False
        )

    expected_compdb = multiple_commands_oneline_compdb + [
        {
            'file': 'bar.cpp',
            'directory': 'data',
            'arguments': [
                'g++',
                'bar.cpp',
                '-o',
                'bar.o'
            ]
        }
    ]
    assert_compdb_equals(compdb_path, expected_compdb)
    output = capsys.readouterr().out
    assert 'Loaded compilation database with 1 entries from ' + filename in output
    assert 'Writing compilation database with 3 entries to ' + compdb_path in output


def assert_compdb_equals(compdb_path, expected_compdb):
    def get_key(item):
        return item['directory'], item['file'], item['arguments']

    try:
        with open(compdb_path, 'r') as instream:
            compdb = json.load(instream)
            assert sorted(compdb, key=get_key) == sorted(expected_compdb, key=get_key)
    finally:
        if os.path.exists(compdb_path):
            os.remove(compdb_path)
