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


import click
import os
import sys
import logging

from . import generate
from .commands import make

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class Options(object):
    """ Simple data class used to store command line options
    shared by all compiledb subcommands"""

    def __init__(self, infile, outfile, build_dir, exclude_files, no_build,
                 verbose, overwrite, strict, add_predefined_macros, use_full_path, command_style):
        self.infile = infile
        self.outfile = outfile
        self.build_dir = build_dir
        self.exclude_files = exclude_files
        self.verbose = verbose
        self.no_build = no_build
        self.overwrite = overwrite
        self.strict = strict
        self.add_predefined_macros = add_predefined_macros
        self.use_full_path = use_full_path
        self.command_style = command_style


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option('-p', '--parse', 'infile', type=click.File('r'),
              help='Build log file to parse compilation commands from.' +
              '(Default: stdin)', required=False, default=sys.stdin)
@click.option('-o', '--output', 'outfile', type=click.File('a+'),
              help="Output file path (Default: compile_commands.json). " +
              'If -f/--overwrite is not specified, this file is updated ' +
              'with the new contents. Use \'-\' to output to stdout',
              required=False, default='compile_commands.json')
@click.option('-d', '--build-dir', 'build_dir', type=click.Path(),
              help="Path to be used as initial build dir", default=os.getcwd())
@click.option('-e', '--exclude', 'exclude_files', multiple=True,
              help="Regular expressions to exclude files.")
@click.option('-n', '--no-build', is_flag=True, default=False,
              help='Only generates compilation db file.')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Print verbose messages.')
@click.option('-f', '--overwrite', is_flag=True, default=False,
              help='Overwrite compile_commands.json instead of just updating it.')
@click.option('-S', '--no-strict', is_flag=True, default=False,
              help='Do not check if source files exist in the file system.')
@click.option('-m', '--macros', 'add_predefined_macros', is_flag=True, default=False,
              help='Add predefined compiler macros to the compilation database. Make sure that ' +
              'all of the used compilers are in your $PATH')
@click.option('--full-path', 'use_full_path', is_flag=True, default=False,
              help='Write full path to the compiler executable.')
@click.option('--command-style', is_flag=True, default=False,
              help='Output compilation database with single "command" '
              'string rather than the default "arguments" list of strings.')
@click.pass_context
def cli(ctx, infile, outfile, build_dir, exclude_files, no_build, verbose, overwrite, no_strict, add_predefined_macros,
        use_full_path, command_style):
    """Clang's Compilation Database generator for make-based build systems.
       When no subcommand is used it will parse build log/commands and generates
       its corresponding Compilation database."""
    log_level = logging.DEBUG if verbose else logging.ERROR
    logging.basicConfig(level=log_level, format=None)
    if ctx.invoked_subcommand is None:
        done = generate(infile, outfile, build_dir, exclude_files, overwrite, not no_strict, add_predefined_macros,
                        use_full_path, command_style)
        exit(0 if done else 1)
    else:
        ctx.obj = Options(infile, outfile, build_dir, exclude_files, no_build, verbose, overwrite, not no_strict,
                          add_predefined_macros, use_full_path, command_style)


# Add subcommands
cli.add_command(make.command)
