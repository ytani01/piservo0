#
# (c) 2025 Yoichi Tanibayashi
#
import click
import pigpio

from .command.cmd_calib import CalibApp
from .command.cmd_servo import CmdServo
from .command.cmd_strctrl import StrCtrlApp
from .core.calibrable_servo import CalibrableServo
from .core.multi_servo import MultiServo
from .helper.str_control import StrControl
from .utils.my_logger import get_logger

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def get_pi(debug=False):
    """
    Initialize and return a pigpio.pi instance.
    If connection fails, log an error and return None.
    """
    log = get_logger(__name__, debug)

    pi = pigpio.pi()
    if not pi.connected:
        log.error("pigpio daemon not connected.")
        return None
    return pi


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

    pi = get_pi(debug)
    if not pi:
        return

    try:
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
calibration tool

* configuration search path:

    Current dir --> Home dir --> /etc
"""
)
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--conf_file", "-c", "-f",
    default=CalibrableServo.DEF_CONF_FILE, show_default=True,
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
        print()
        print("Error: Please specify GPIO pins.")
        print()
        print("  e.g. piservo0 calib 17 27")
        print()
        print(f"{ctx.get_help()}")
        return

    pi = get_pi(debug)
    if not pi:
        return

    app = None
    try:
        app = CalibApp(pi, pins, conf_file, debug=debug)
        app.main()

    except (EOFError, KeyboardInterrupt):
        pass

    except Exception as _e:
        log.error("%s: %s", type(_e).__name__, _e)

    finally:
        if pi:
            app.end()
            pi.stop()


@cli.command(
    help="""
Multi Servo, String control
"""
)
@click.argument("pins", type=int, nargs=-1)
# ThreadMultiServo options
@click.option(
    "--conf_file", "-c", default=CalibrableServo.DEF_CONF_FILE,
    show_default=True, help="Config file path"
)
# StrControl options
@click.option(
    "--move_sec", "-m", type=float, default=StrControl.DEF_MODE_SEC,
    show_default=True, help="estimated move time(sec)"
)
@click.option(
    "--step_n", "-s", type=int, default=MultiServo.DEF_STEP_N,
    show_default=True, help="Step Number"
)
@click.option(
    "--angle_unit", "-u", type=float, default=StrControl.DEF_ANGLE_UNIT,
    show_default=True, help="Angle Unit"
)
@click.option(
    "--angle_factor", "-f", type=str, default="-1 -1 1 1",
    show_default=True, help="Angle Factor"
)
# for debug
@click.option(
    "--debug", "-d", is_flag=True, default=False, help="debug flag"
)
@click.pass_context
def strctrl(
    ctx, pins, conf_file, move_sec, step_n, angle_unit, angle_factor, debug
):
    """strctrl"""
    log = get_logger(__name__, debug)
    log.debug("pins=%s,conf_file=%s", pins, conf_file)
    log.debug("move_sec=%s, step_n=%s", move_sec, step_n)

    angle_factor = [float(a) for a in angle_factor.split()]
    log.debug("angle_unit=%s, angle_factor=%s", angle_unit, angle_factor)

    if not pins:
        print()
        print("Error: Please specify GPIO pins.")
        print()
        print("  e.g. piservo0 calib 17 27")
        print()
        print(f"{ctx.get_help()}")
        return

    _pi = get_pi(debug)
    if not _pi:
        return

    _app = None
    try:
        _app = StrCtrlApp(
            _pi, pins, conf_file=conf_file,
            move_sec=move_sec, step_n=step_n,
            angle_unit=angle_unit, angle_factor=angle_factor,
            debug=debug
        )
        _app.main()

    except (EOFError, KeyboardInterrupt):
        pass

    except Exception as _e:
        log.error("%s: %s", type(_e).__name__, _e)

    finally:
        if _pi:
            _app.end()
            _pi.stop()
