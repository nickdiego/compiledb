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
nonexistent_files = ['compile_commands.json', 'nonexistent.json']
stdout_filenames = ['-', '']


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


@pytest.mark.parametrize('output_filename', stdout_filenames)
def test_load_compdb_ignores_stdout_filename(capsys, output_filename):
    assert load_json_compdb(output_filename, verbose=True) == []
    assert capsys.readouterr().out == ''


@pytest.mark.parametrize('output_filename', nonexistent_files)
def test_generate_input_file_not_exist_no_overwrite(capsys, output_filename):
    assert_generate_is_true(output_filename, overwrite=False)
    assert_compdb_file_equals(output_filename, multiple_commands_oneline_compdb)
    output = capsys.readouterr().out
    assert 'Failed to read previous ' + output_filename in output
    assert 'Writing compilation database with 2 entries to ' + output_filename in output


@pytest.mark.parametrize('output_filename', nonexistent_files)
def test_generate_input_file_not_exist_overwrite(capsys, output_filename):
    assert_generate_is_true(output_filename, overwrite=True)
    assert_compdb_file_equals(output_filename, multiple_commands_oneline_compdb)
    output = capsys.readouterr().out
    assert 'Failed to read previous ' + output_filename not in output
    assert 'Writing compilation database with 2 entries to ' + output_filename in output


def test_generate_input_file_exists_no_overwrite(capsys):
    input_filename = os.path.join(data_dir, 'compile_commands2.json')
    output_filename = 'compile_commands2.json'
    shutil.copy(input_filename, output_filename)

    assert_generate_is_true(output_filename, overwrite=False)

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
    assert_compdb_file_equals(output_filename, expected_compdb)
    output = capsys.readouterr().out
    assert 'Loaded compilation database with 1 entries from ' + output_filename in output
    assert 'Writing compilation database with 3 entries to ' + output_filename in output


def test_generate_input_file_exists_overwrite(capsys):
    input_filename = os.path.join(data_dir, 'compile_commands2.json')
    output_filename = 'compile_commands2.json'
    shutil.copy(input_filename, output_filename)

    assert_generate_is_true(output_filename, overwrite=True)

    assert_compdb_file_equals(output_filename, multiple_commands_oneline_compdb)
    output = capsys.readouterr().out
    assert 'Loaded compilation database with 1 entries from ' + output_filename not in output
    assert 'Writing compilation database with 2 entries to ' + output_filename in output


@pytest.mark.parametrize('output_filename', ['-', ''])
@pytest.mark.parametrize('overwrite', [False, True])
def test_generate_output_stdout(capsys, output_filename, overwrite):
    try:
        assert_generate_is_true(output_filename, overwrite=overwrite)
        assert not os.path.exists(output_filename)
        output = capsys.readouterr().out
        assert 'Writing compilation database with 2 entries to <stdout>' in output
        
        # Find where the JSON file starts and ends and decode it
        start_index = output.index('[')
        end_index = output.rindex(']') + 1
        compdb = json.loads(output[start_index:end_index])

        assert_compdb_equals(compdb, multiple_commands_oneline_compdb)
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)


def assert_generate_is_true(output_filename, overwrite):
    with input_file('multiple_commands_oneline') as instream:
        assert generate(
            infile=instream,
            outfile=output_filename,
            build_dir=os.getcwd(),
            exclude_files=[],
            verbose=True,
            overwrite=overwrite,
            strict=False
        )

def assert_compdb_file_equals(compdb_path, expected_compdb):
    try:
        with open(compdb_path, 'r') as instream:
            compdb = json.load(instream)
            assert_compdb_equals(compdb, expected_compdb)
    finally:
        if os.path.exists(compdb_path):
            os.remove(compdb_path)


def assert_compdb_equals(compdb, expected_compdb):
    def get_key(item):
        return item['directory'], item['file'], item['arguments']

    assert sorted(compdb, key=get_key) == sorted(expected_compdb, key=get_key)
