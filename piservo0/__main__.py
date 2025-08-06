#
# (c) 2025 Yoichi Tanibayashi
#
""" __main__.py """
import os

import click
import pigpio
import uvicorn

from .command.cmd_calib import CalibApp
from .command.cmd_servo import CmdServo
from .command.cmd_strctrl import StrCtrlApp
from .command.cmd_webclient import WebClientApp
from .core.calibrable_servo import CalibrableServo
from .core.multi_servo import MultiServo
from .helper.str_control import StrControl
from .utils.my_logger import get_logger

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def get_pi(debug=False):
    """Initialize and return a pigpio.pi instance.

    If connection fails, log an error and return None.
    """
    _log = get_logger(__name__, debug)

    pi = pigpio.pi()
    if not pi.connected:
        _log.error("pigpio daemon not connected.")
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
    """CLI top."""
    cmd_name = ctx.info_name
    subcmd_name = ctx.invoked_subcommand

    _log = get_logger(cmd_name, debug)

    _log.debug("cmd_name=%s, subcmd_name=%s", cmd_name, subcmd_name)

    if subcmd_name is None:
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
    """servo command."""
    _log = get_logger(__name__, debug)
    _log.debug('pin=%s, pulse="%s", sec=%s', pin, pulse, sec)

    pi = get_pi(debug)
    if not pi:
        return

    app = None
    try:
        app = CmdServo(pi, pin, pulse, sec, debug=debug)
        app.main(ctx)

    except Exception as _e:
        _log.error("%s: %s", type(_e).__name__, _e)

    finally:
        if app:
            app.end()
        if pi:
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
    """calib command."""
    _log = get_logger(__name__, debug)
    _log.debug("pins=%s,conf_file=%s", pins, conf_file)

    cmd_name = ctx.command.name
    _log.debug("cmd_name=%s", cmd_name)

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
        _log.error("%s: %s", type(_e).__name__, _e)

    finally:
        if app:
            app.end()
        if pi:
            pi.stop()


@cli.command(
    help="""
Multi Servo, String control
"""
)
@click.argument("pins", type=int, nargs=-1)
# ThreadMultiServo options
@click.option(
    "--conf_file", "-c", type=str, default=CalibrableServo.DEF_CONF_FILE,
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
    """strctrl."""
    _log = get_logger(__name__, debug)
    _log.debug("pins=%s,conf_file=%s", pins, conf_file)
    _log.debug("move_sec=%s, step_n=%s", move_sec, step_n)

    angle_factor = [float(a) for a in angle_factor.split()]
    _log.debug("angle_unit=%s, angle_factor=%s", angle_unit, angle_factor)

    cmd_name = ctx.command.name
    _log.debug("cmd_name=%s", cmd_name)

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
        _log.error("%s: %s", type(_e).__name__, _e)

    finally:
        if _app:
            _app.end()
        if _pi:
            _pi.stop()


@cli.command(
    help="""
String API Server
"""
)
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--server_host", "-s", type=str, default="0.0.0.0", show_default=True,
    help="server hostname or IP address"
)
@click.option(
    "--port", "-p", type=int, default=8000, show_default=True,
    help="port number"
)
@click.option(
    "--angle-factor", "-a", type=str, default='', show_default=True,
    help="Angle factors (e.g. '-1,-1,1,1')"
)
# for debug
@click.option(
    "--debug", "-d", is_flag=True, default=False, help="debug flag"
)
@click.pass_context
def web_str_api(ctx, pins, server_host, port, angle_factor, debug):
    """Web API Client."""
    cmd_name = ctx.command.name

    _log = get_logger(__name__, debug)
    _log.debug("cmd_name=%s", cmd_name)
    _log.debug("pins=%s", pins)
    _log.debug("server_host=%s, port=%s", server_host, port)
    _log.debug("angle_factor=%s", angle_factor)

    #
    # check `pins`
    #
    if pins:
        os.environ["PISERVO0_PINS"] = ','.join([str(p) for p in pins])
    else:
        print()
        print("Error: Please specify GPIO pins.")
        print()
        print("    e.g. piservo0 {cmd_name} 17 27")
        print()
        print(f"{ctx.get_help()}")
        print()
        return

    #
    # check `angle_factor`
    #
    if not angle_factor:
        angle_factor = ','.join(['1'] * len(pins))
        _log.debug("angle_factor=%a", angle_factor)

    if len(angle_factor.split(",")) != len(pins):
        print()
        print(f"Error: Invalid angle_factor length: '{angle_factor}'")
        print()
        print(f"    pins={pins}: length must be {len(pins)}")
        print()
        print(f"{ctx.get_help()}")
        print()
        return

    os.environ["PISERVO0_ANGLE_FACTOR"] = angle_factor

    os.environ["PISERVO0_DEBUG"] = "1" if debug else "0"

    uvicorn.run(
        "piservo0.web.str_api:app", host=server_host, port=port, reload=True
    )


@cli.command(
    help="""
String API Client
"""
)
@click.argument("cmdline", type=str, nargs=-1)
@click.option(
    "--server_host", "-s", type=str, default="localhost", show_default=True,
    help="server hostname or IP address"
)
@click.option(
    "--port", "-p", type=int, default=8000, show_default=True,
    help="port number"
)
# for debug
@click.option(
    "--debug", "-d", is_flag=True, default=False, help="debug flag"
)
@click.pass_context
def web_client(ctx, cmdline, server_host, port, debug):
    """Web API Client."""
    _log = get_logger(__name__, debug)
    _log.debug("server_host=%s, port=%s", server_host, port)

    cmdline = " ".join(cmdline)
    _log.debug("cmdline=%a", cmdline)

    cmd_name = ctx.command.name
    _log.debug("cmd_name=%s", cmd_name)

    _app = WebClientApp(server_host, port, cmdline, debug)
    try:
        _app.main()

    except (KeyboardInterrupt, EOFError):
        print("\nBye\n")

    finally:
        _app.end()


@cli.command(
    help="""
JSON API Server
"""
)
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--server_host", "-s", type=str, default="0.0.0.0", show_default=True,
    help="server hostname or IP address"
)
@click.option(
    "--port", "-p", type=int, default=8000, show_default=True,
    help="port number"
)
# for debug
@click.option(
    "--debug", "-d", is_flag=True, default=False, help="debug flag"
)
@click.pass_context
def web_json_api(ctx, pins, server_host, port, debug):
    """Web API Client."""
    cmd_name = ctx.command.name

    _log = get_logger(__name__, debug)
    _log.debug("cmd_name=%s", cmd_name)
    _log.debug("pins=%s", pins)
    _log.debug("server_host=%s, port=%s", server_host, port)

    if pins:
        os.environ["PISERVO0_PINS"] = ','.join([str(p) for p in pins])
    else:
        print()
        print("Error: Please specify GPIO pins.")
        print()
        print(f"  e.g. piservo0 {cmd_name} 17 27")
        print()
        print(f"{ctx.get_help()}")
        print()
        return

    os.environ["PISERVO0_DEBUG"] = "1" if debug else "0"

    uvicorn.run(
        "piservo0.web.json_api:app", host=server_host, port=port, reload=True
    )
