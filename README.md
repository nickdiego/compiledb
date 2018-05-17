# Compilation Database Generator

[![CircleCI](https://circleci.com/gh/nickdiego/compiledb-generator/tree/master.svg?style=svg)](https://circleci.com/gh/nickdiego/compiledb-generator/tree/master)

Tool for generating [clang/LLVM's JSON Compilation Database][compdb] file for GNU
`make`-based build systems.

It's aimed mainly at non-cmake (cmake already generates compilation database)
large codebases. Inspired by projects like [YCM-Generator][ycm-gen] and [Bear][bear],
but it's supposed to be faster (mainly with large projects), since it **doesn't need a
clean build** (as the current available tools do) to generate the compilation database
file, to achieve this it uses the make options such as `-Bnk` to extract the compile
commands. Also, it's more cross-compiling friendly than YCM-generator's fake-toolchanin
approach.

## Installation

```
# pip install compiledb
```
- _Supports Python 2 and 3 (tested mainly with 2.7 and 3.6 versions)_
- For bash completion support, add the content of `sh-completion/compiledb.bash` file
  to your `.bashrc` file, for example.
- _ZSH completion coming soon :)_

## Usage

`compiledb` provides a `make` python wrapper script which, besides to execute the make
build command, updates the JSON compilation database file corresponding to that build
command, resulting in a command-line interface similar to [Bear][bear].

To generate `compile_commands.json` file using compiledb-generator's "make wrapper" script,
executing Makefile target `all`:
```bash
$ compiledb make all -j4
```

Generate `compile_commands.json` file using compiledb-generator's "make wrapper" script,
using `custom_makefile.mk` as main Makefile:
```bash
$ compiledb make -f custom_makefile.mk
```

Also, `compiledb` base command can be used to parse compile commands from an arbitrary text
file (or stdin), assuming it has a build log, and generates the JSON Compilation database.

For example, to parse a build log file and prints the compilation database to `compile_commands.json`
file, use the following command.
```bash
$ compiledb -i build-log.txt
```

## Testing / Contributing

I've implemented it basically because I needed to index some AOSP's modules for navigating
and studying purposes (after having no satisfatory results with current tools such as
[YCM-Generator][ycm] and [Bear][bear]). So I've reworked YCM-Generator, which resulted in
`compiledb-gen-parser` and used successfully to generate compilation database for some AOSP
modules in ~1min running in a [Docker][docker] container and then I've been able to use some
great tools such as _Vim + [YouCompleteMe][ycm] + [rtags][rtags] + [chromatica.nvim][chrom]_
with the codebase.

- [Vim][vim] + [YouCompleteMe][ycm] + [rtags][rtags] + [chromatica.nvim][chrom]
- [Neovim][neovim] + [LanguageClient-neovim][lsp] + [cquery][cquery] + [deoplete][deoplete]

Notice:
- _Windows not supported yet (at least not tested yet in Cygwin/MinGW)_
- _Tested only on Linux (Arch Linux) so far_

Patches are always welcome :)

## License
GNU GPLv3

[compdb]: https://clang.llvm.org/docs/JSONCompilationDatabase.html
[ycm]: https://github.com/Valloric/YouCompleteMe
[rtags]: https://github.com/Andersbakken/rtags
[chrom]: https://github.com/arakashic/chromatica.nvim
[ycm-gen]: https://github.com/rdnetto/YCM-Generator
[bear]: https://github.com/rizsotto/Bear
[aosp]: https://source.android.com/
[docker]: https://www.docker.com/
[vim]: https://www.vim.org/
[neovim]: https://neovim.io/
[lsp]: https://github.com/autozimu/LanguageClient-neovim
[cquery]: https://github.com/cquery-project/cquery
[deoplete]: https://github.com/Shougo/deoplete.nvim
