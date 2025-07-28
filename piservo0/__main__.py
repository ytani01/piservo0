#
# (c) 2025 Yoichi Tanibayashi
#
import click
import pigpio

from piservo0 import get_logger

from .cmd_calib import CalibApp
from .cmd_multi import CmdMulti
from .cmd_servo import CmdServo

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

    try:
        pi = pigpio.pi()
        if not pi.connected:
            log.error("pigpio daemon not connected.")
            return
        app = CmdServo(pi, pin, pulse, sec, debug=debug)

    except Exception as _e:
        log.error("%s: %s", type(_e).__name__, _e)
        return

    try:
        app.main(ctx)

    except Exception as _e:
        log.warning("%s: %s", type(_e).__name__, _e)

    finally:
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

    try:
        app = CalibApp(pins, conf_file, debug=debug)

    except Exception as _e:
        log.error("%s: %s", type(_e).__name__, _e)
        return

    try:
        app.main()

    except (EOFError, KeyboardInterrupt) as _e:
        log.debug("%s: %s", type(_e).__name__, _e)

    except Exception as _e:
        log.error("%s: %s", type(_e).__name__, _e)

    finally:
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

    try:
        pi = pigpio.pi()
        if not pi.connected:
            log.error("pigpio daemon not connected.")
            return
        app = CmdMulti(pi, pin, conf_file, sec, debug=debug)

    except Exception as _e:
        log.error("%s: %s", type(_e).__name__, _e)
        return

    try:
        app.main(ctx)

    except (EOFError, KeyboardInterrupt) as _e:
        log.debug("%s: %s", type(_e).__name__, _e)

    except Exception as _e:
        log.error("%s: %s", type(_e).__name__, _e)

    finally:
        app.end()
        pi.stop()