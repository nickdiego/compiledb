#!/usr/bin/env python
#
#   compiledb-generator: Tool for generating LLVM Compilation Database
#   files for make-based build systems.
#
#   Copyright (c) 2019 Nick Diego Yamane <nick.diego@gmail.com>
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
import shutil
import json
import pytest
import sys
from os.path import basename
from compiledb import load_json_compdb, generate
from tests.common import input_file, output_file, data_dir, full_path


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
nonexistent_files = ['compile_commands.json', 'nonexistent.json']


def test_load_compdb_path_file_exists(capsys):
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
        with input_file('compile_commands.json') as outfile:
            assert load_json_compdb(outfile) == expected_compdb
            assert (
                'Loaded compilation database with 1 entries from compile_commands.json'
                in capsys.readouterr().out
            )
    finally:
        os.chdir(orig_pwd)


def test_load_compdb_ignores_stdout_filename(capsys):
    assert load_json_compdb(sys.stdout, verbose=True) == []
    assert capsys.readouterr().out == ''


def test_generate_input_file_exists_no_overwrite(capsys):
    shutil.copy(full_path('compile_commands2.json'),
                full_path('result.json'))
    with output_file("result.json") as outfile:
        assert_generate_is_true(outfile, overwrite=False)

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
    assert_compdb_file_equals(outfile.name, expected_compdb)
    output = capsys.readouterr().out
    assert 'Loaded compilation database with 1 entries from ' + basename(outfile.name) in output
    assert 'Writing compilation database with 3 entries to ' + basename(outfile.name) in output


def test_generate_input_file_exists_overwrite(capsys):
    shutil.copy(full_path('compile_commands2.json'),
                full_path('result.json'))
    with output_file("result.json") as outfile:
        assert_generate_is_true(outfile, overwrite=True)

    assert_compdb_file_equals(outfile.name, multiple_commands_oneline_compdb)
    output = capsys.readouterr().out
    assert 'Loaded compilation database with 1 entries from ' + basename(outfile.name) not in output
    assert 'Writing compilation database with 2 entries to ' + basename(outfile.name) in output


@pytest.mark.parametrize('overwrite', [False, True])
def test_generate_output_stdout(capsys, overwrite):
    assert_generate_is_true(sys.stdout, overwrite=overwrite)
    assert not os.path.exists("<stdout>")
    output = capsys.readouterr().out
    assert 'Writing compilation database with 2 entries to <stdout>' in output

    # Find where the JSON file starts and ends and decode it
    start_index = output.index('[')
    end_index = output.rindex(']') + 1
    compdb = json.loads(output[start_index:end_index])

    assert_compdb_equals(compdb, multiple_commands_oneline_compdb)


def assert_generate_is_true(outstream, overwrite):
    with input_file('multiple_commands_oneline.txt') as instream:
        assert generate(
            infile=instream,
            outfile=outstream,
            build_dir=os.getcwd(),
            exclude_files=[],
            verbose=True,
            overwrite=overwrite,
            strict=False
        )


def assert_compdb_file_equals(outfile_path, expected_compdb):
    try:
        with open(outfile_path, 'r') as instream:
            compdb = json.load(instream)
            assert_compdb_equals(compdb, expected_compdb)
    finally:
        if os.path.exists(outfile_path):
            os.remove(outfile_path)


def assert_compdb_equals(compdb, expected_compdb):
    def get_key(item):
        return item['directory'], item['file'], item['arguments']

    assert sorted(compdb, key=get_key) == sorted(expected_compdb, key=get_key)
