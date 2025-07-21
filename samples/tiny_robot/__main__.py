#
# (c) 2025 Yoichi Tanibayashi
#
import click
from piservo0 import get_logger

from .demo1 import demo1
from .manual import manual


# clickで、'-h'もヘルプオプションするために
CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS,
             help="Tiny Robot")
@click.option('-debug', '-d', is_flag=True, help="debug flag")
@click.pass_context
def cli(ctx, debug):
    """ CLI top """

    _log = get_logger(__name__, debug)
    _log.debug('ctx=%s', dir(ctx))

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


cli.add_command(demo1)
cli.add_command(manual)


if __name__ == '__main__':
    cli()