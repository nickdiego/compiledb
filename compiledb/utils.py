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
from __future__ import print_function

import sys


def input_file(path):
    return sys.stdin if path is None else open(path, "r")


def output_file(path):
    return sys.stdout if path is None else open(path, "w")


def msg(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def unescape(s):
    return s.encode().decode('unicode_escape')

# ex: ts=2 sw=4 et filetype=python

