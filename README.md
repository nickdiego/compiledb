# Compilation Database Generator

[![CircleCI](https://circleci.com/gh/nickdiego/compiledb-generator/tree/master.svg?style=svg)](https://circleci.com/gh/nickdiego/compiledb-generator/tree/master)

Tool for generating [clang/LLVM's JSON Compilation Database][compdb] file for
`make`-based build systems.

It's aimed mainly at non-cmake (cmake already generates compilation database)
large codebases. Inspired by projects like [YCM-Generator][ycm-gen] and [Bear][bear],
but it's supposed to be faster (mainly with large projects), since it **doesn't need a
clean build** (as the current available tools do) to get the compile commands, to achieve
this it uses the make options `-Bnk` to generate the compilation database file. Also,
it's more cross-compiling friendly than YCM-generator's fake-toolchanin approach.

## Dependencies

- Python >= 2.7
- GNU make _( >= version?)_

## Usage

Generate `compile_commands.json` using compiledb-generator's "make wrapper" script,
executing Makefile target `all`:
```bash
$ compiledb-gen-make all > compile_commands.json
```

Generate `compile_commands.json` using compiledb-generator's "make wrapper" script,
using `custom_makefile.mk` as main Makefile:
```bash
$ compiledb-gen-make -f custom_makefile.mk > compile_commands.json
```

Genrate `compile_commands.json` for some AOSP module (assuming you're running
the script from the root of [AOSP][aosp] tree):
```bash
$ compiledb-gen-aosp -o compile_commands.json <aosp/module/path>
```

Parse a build log file and prints the compilation database to stdout:
```bash
$ compiledb-gen-parser . < build-log.txt
```

## Testing / Contributing

I've implemented it basically because I needed to index some AOSP's
modules for navigating and studying purposes (after having no satisfatory results with
current tools such as [YCM-Generator][ycm] and [Bear][bear]). So I've reworked
YCM-Generator, which resulted in `compiledb-gen-parser` and used successfully to
generate compilation database for some AOSP modules in ~1min running in a [Docker][docker]
container and then some great tools may be used for studying and analysis purposes, such as:

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
