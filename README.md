# Compilation Database Generator

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
container and then I've been able to use some great tools such as _Vim + [YouCompleteMe][ycm] +
[rtags][rtags] + [chromatica.nvim][chrom]_ with the codebase.

Even though it's working ok in my environment, with AOSP 5.0, etc, it's still a
work in progress and not well tested yet. So, give it a try! Report the issues you
got, and maybe send some PR's :)

- _Windows not supported yet (at least not tested yet in Cygwin/MinGW)_
- _Tested only on Linux (Arch Linux) so far_

## License
GNU GPLv3

[compdb]: https://clang.llvm.org/docs/JSONCompilationDatabase.html
[ycm]: https://github.com/Valloric/YouCompleteMe
[rtags]: https://github.com/Andersbakken/rtags
[chrom]: https://github.com/arakashic/chromatica.nvim
[ycm-gen]: https://github.com/rdnetto/YCM-Generator
[bear]: https://github.com/rizsotto/Bear
[aosp]: https://source.android.com/
