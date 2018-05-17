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


import click
import os
import sys

from . import generate
from .commands import make

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class Options(object):
    """ Simple data class used to store command line options
    shared by all compiledb subcommands"""

    def __init__(self, infile, outfile, build_dir, inc_prefix,
                 exclude_list, no_build, verbose):
        self.infile = infile
        self.outfile = outfile
        self.build_dir = build_dir
        self.inc_prefix = inc_prefix
        self.exclude_list = exclude_list
        self.verbose = verbose
        self.no_build = no_build


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option('-p', '--parse', 'infile', type=click.File('r'),
              help='Build log file to parse compilation commands from.' +
              '(Default: stdin)', required=False, default=sys.stdin)
@click.option('-o', '--output', 'outfile', type=click.File('w'),
              help="Output file path (Default: std output)",
              required=False, default='compile_commands.json')
@click.option('-d', '--build-dir', 'build_dir', type=click.Path(),
              help="Path to be used as initial build dir", default=os.getcwd())
@click.option('-i', '--include-prefix', 'inc_prefix', type=click.Path(),
              help="Path to be used as include base directory")
@click.option('-e', '--exclude', 'exclude_list', multiple=True,
              help="Regular expressions to exclude files.")
@click.option('-n', '--no-build', is_flag=True, default=False,
              help='Only generates compilation db file.')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Print verbose messages.')
@click.pass_context
def cli(ctx, infile, outfile, build_dir, inc_prefix, exclude_list, no_build, verbose):
    """Clang's Compilation Database generator for make-based build systems.
       When no subcommand is used it will parse build log/commands and generates
       its corresponding Compilation database."""
    assert not sys.platform.startswith("win32")
    if ctx.invoked_subcommand is None:
        generate(infile, outfile, build_dir, inc_prefix, exclude_list, verbose)
    else:
        ctx.obj = Options(infile, outfile, build_dir, inc_prefix, exclude_list,
                          no_build, verbose)


# Add subcommands
cli.add_command(make.command)
