import logging
import os
from subprocess import PIPE

from shutilwhich import which

from compiledb.utils import popen

_logger = logging.getLogger(__name__)


class Compiler:
    def __init__(self, name="gcc"):
        # Name of the compiler executable
        self._name = name

        # Full path to the compiler executable
        self._full_path = self._find_full_path()

        # Supported languages by the compiler
        self._languages = {
            "c": {
                "extensions": ["c"]
            },
            "c++": {
                "extensions": ["cpp", "cc", "cx", "cxx"],
            },
        }

        # Keep a list of macros for each language since, for example, gcc can be used both for C and C++ sources.
        self._predefined_macros = {
            # language: ["-DMACRO1", "-DMACRO2=1"]
        }

    def __str__(self):
        return self.name

    def _find_full_path(self):
        """Get a full path to the compiler executable."""
        full_path = which(self.name)

        if full_path is None:
            full_path = self.name

        return full_path

    def _get_language(self, arguments, source_file):
        """Attempt to find the language from flags or the source name."""
        default = "c"

        for arg_idx, arg in enumerate(arguments):
            if arg == "-x" and arg_idx < len(arguments) - 1:
                return arguments[arg_idx + 1]

            if "-std=" in arg:
                if "++" in arg:
                    return "c++"
                else:
                    return default

        _, extension = os.path.splitext(source_file)

        if extension in self._languages["c++"]["extensions"]:
            return "c++"
        else:
            return default

    def _add_predefined_macros(self, language):
        """Add a list of macros predefined by the compiler for future use."""
        self._predefined_macros[language] = []
        # Dump all predefined compiler macros
        cmd = "echo | " + self.name + " -x " + language + " -dM -E -"

        try:
            pipe = popen(cmd, stdout=PIPE)
        except (OSError, ValueError) as e:
            _logger.error(e)
            return

        for line in pipe.stdout:
            columns = line.split()
            size = len(columns)

            if size <= 1:
                continue
            elif size == 2:
                def_arg = "-D" + columns[1]
            else:
                def_arg = "-D" + columns[1] + "=" + " ".join(columns[2:])

            self._predefined_macros[language].append(def_arg)

        pipe.wait()

    @property
    def name(self):
        return self._name

    @property
    def full_path(self):
        return self._full_path

    def get_predefined_macros(self, arguments, source_file):
        """Return a list of macros predefined by the compiler."""
        language = self._get_language(arguments, source_file)

        if language not in self._predefined_macros:
            self._add_predefined_macros(language)

        return self._predefined_macros[language]


_compilers = []


def get_compiler(name):
    c = next((compiler for compiler in _compilers if name == compiler.name), None)

    if c is None:
        c = Compiler(name)
        _compilers.append(c)

    return c
