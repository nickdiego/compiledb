import click
from subprocess import call, PIPE, Popen
from sys import exit, stdout, stderr, version_info

from compiledb import generate


if version_info[0] >= 3:  # Python 3
    def popen(cmd, encoding='utf-8', **kwargs):
        return Popen(cmd, encoding=encoding, **kwargs)
else:  # Python 2
    def popen(cmd, encoding='utf-8', **kwargs):
        return Popen(cmd, **kwargs)


@click.command(name='make', context_settings=dict(ignore_unknown_options=True))
@click.option('-c', '--cmd', 'make_cmd', nargs=1, required=False,
              help="Command to be used as make executable.")
@click.argument('make_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def command(ctx, make_cmd, make_args):
    """Generates compilation database file for an arbitrary GNU Make command.
     Acts like a make wrapper, forwarding all MAKE_ARGS to make command"""

    make_cmd = make_cmd or 'make'
    logging_mode_flags = "-Bnkw"

    options = ctx.obj

    if not options.no_build:
        cmd = [make_cmd] + list(make_args)
        print("## Building [{}]...".format(' '.join(cmd)))
        ret = call(cmd, stdout=stdout, stderr=stderr)
        print()
        if ret != 0:
            exit(1)

    cmd = [make_cmd, logging_mode_flags] + list(make_args)
    pipe = popen(cmd, stdout=PIPE, encoding='utf-8')
    options.infile = pipe.stdout
    generate(**vars(options))
    pipe.wait()
