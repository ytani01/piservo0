#
# (c) 2025 Yoichi Tanibayashi
#
import click
import pigpio

from .utils.my_logger import get_logger
from .command.cmd_servo import CmdServo
from .command.cmd_multi import CmdMulti
from .command.cmd_calib import CalibApp

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="""
pyservo0 command
"""
)
@click.option("-d", "--debug", is_flag=True, help="debug flag")
@click.pass_context
def cli(ctx, debug):
    """CLI top"""
    subcmd = ctx.invoked_subcommand
    log = get_logger(__name__, debug)
    log.debug("subcmd=%s", subcmd)

    if subcmd is None:
        print(f"{ctx.get_help()}")


@cli.command(
    help="""
servo command"""
)
@click.argument("pin", type=int, nargs=1)
@click.argument("pulse", type=str, nargs=1)
@click.option(
    "--sec", "-t", "-s", type=float,
    default=1.0, show_default=True,
    help="sec",
)
@click.option("--debug", "-d", is_flag=True, default=False, help="debug flag")
@click.pass_context
def servo(ctx, pin, pulse, sec, debug):
    """servo command"""
    log = get_logger(__name__, debug)
    log.debug('pin=%s, pulse="%s", sec=%s', pin, pulse, sec)

    pi = None
    try:
        pi = pigpio.pi()
        if not pi.connected:
            log.error("pigpio daemon not connected.")
            return
        app = CmdServo(pi, pin, pulse, sec, debug=debug)
        app.main(ctx)

    except Exception as e:
        log.error("%s: %s", type(e).__name__, e)

    finally:
        if pi:
            app.end()
            pi.stop()


@cli.command(
    help="""
calibration tool"""
)
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--conf_file", "-c", "-f",
    default="./servo.json", show_default=True,
    help="Config file path"
)
@click.option(
    "--debug", "-d", is_flag=True, default=False, help="debug flag"
)
@click.pass_context
def calib(ctx, pins, conf_file, debug):
    """calib command"""
    log = get_logger(__name__, debug)
    log.debug("pins=%s,conf_file=%s", pins, conf_file)

    if not pins:
        log.error("No GPIO pins specified.")
        print(
            "Error: Please specify GPIO pins. e.g. `piservo0 calib 17 27`"
        )
        return

    app = None
    try:
        app = CalibApp(pins, conf_file, debug=debug)
        app.main()

    except (EOFError, KeyboardInterrupt):
        pass
    except Exception as e:
        log.error("%s: %s", type(e).__name__, e)

    finally:
        if app:
            app.end()


@cli.command(
    help="""
multi servo controller"""
)
@click.argument("pin", type=int, nargs=-1)
@click.option(
    "--conf_file", "--file", "-c", "-f", type=str,
    default="./servo.json", show_default=True,
    help="config file"
)
@click.option(
    "--sec", "-t", "-s", type=float,
    default=1, show_default=True,
    help="move sec"
)
@click.option("--debug", "-d", is_flag=True, help="debug flag")
@click.pass_context
def multi(ctx, pin, conf_file, sec, debug):
    """servo command"""
    log = get_logger(__name__, debug)
    log.debug("pin=%s,conf_file=%s,sec=%s", pin, conf_file, sec)

    pi = None
    try:
        pi = pigpio.pi()
        if not pi.connected:
            log.error("pigpio daemon not connected.")
            return
        app = CmdMulti(pi, pin, conf_file, sec, debug=debug)
        app.main(ctx)

    except (EOFError, KeyboardInterrupt):
        pass
    except Exception as e:
        log.error("%s: %s", type(e).__name__, e)

    finally:
        if pi:
            app.end()
            pi.stop()
