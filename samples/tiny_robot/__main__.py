#
# (c) 2025 Yoichi Tanibayashi
#
import click

from piservo0 import get_logger

from .demo1 import demo1
from .exec import exec
from .manual import manual
from .thr_manual import thr_manual

# clickで、'-h'もヘルプオプションするために
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="Tiny Robot",
)
@click.option("-debug", "-d", is_flag=True, help="debug flag")
@click.pass_context
def cli(ctx, debug):
    """CLI top"""

    __log = get_logger(__name__, debug)
    __log.debug("ctx=%s", dir(ctx))

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


cli.add_command(demo1)
cli.add_command(manual)
cli.add_command(thr_manual)
cli.add_command(exec)


if __name__ == "__main__":
    cli()
