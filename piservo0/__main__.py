#
# (c) 2025 Yoichi Tanibayashi
#
"""__main__.py"""
import os

import click
import pigpio
import uvicorn

from . import __version__, click_common_opts, get_logger
from .command.cmd_apiclient import CmdApiClient
from .command.cmd_calib import CalibApp
from .command.cmd_servo import CmdServo
from .command.cmd_strclient import CmdStrClient
from .core.calibrable_servo import CalibrableServo


def get_pi(debug=False):
    """Initialize and return a pigpio.pi instance.

    If connection fails, log an error and return None.
    """
    __log = get_logger(__name__, debug)

    pi = pigpio.pi()
    if not pi.connected:
        __log.error("pigpio daemon not connected.")
        return None
    return pi


@click.group(invoke_without_command=True, help="pyservo0 command")
@click_common_opts(__version__)
def cli(ctx, debug):
    """CLI top."""
    cmd_name = ctx.info_name
    subcmd_name = ctx.invoked_subcommand

    ___log = get_logger(cmd_name, debug)

    ___log.debug("cmd_name=%s, subcmd_name=%s", cmd_name, subcmd_name)

    if subcmd_name is None:
        print(ctx.get_help())


@cli.command(help="servo command")
@click.argument("pin", type=int, nargs=1)
@click.argument("pulse", type=str, nargs=1)
@click.option(
    "--wait-sec", "-s", "-w", type=float, default=0.8, show_default=True,
    help="wait sec"
)
@click_common_opts(__version__)
def servo(
    ctx, pin: int, pulse: int, wait_sec: float, debug: bool
) -> None:
    """servo command."""
    __log = get_logger(__name__, debug)
    __log.debug('pin=%s, pulse="%s", wait_sec=%s', pin, pulse, wait_sec)

    cmd_name = ctx.command.name
    __log.debug("cmd_name=%s", cmd_name)

    pi = get_pi(debug)
    if not pi:
        return

    app = None
    try:
        app = CmdServo(pi, pin, pulse, wait_sec, debug=debug)
        app.main(ctx)

    except Exception as _e:
        __log.error("%s: %s", type(_e).__name__, _e)

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
@click.argument("pin", type=int, nargs=1)
@click.option(
    "--conf_file", "-c", "-f", type=str,
    default=CalibrableServo.DEF_CONF_FILE, show_default=True,
    help="Config file"
)
@click_common_opts(__version__)
def calib(ctx, pin, conf_file, debug):
    """calibration command."""
    __log = get_logger(__name__, debug)
    __log.debug("pin=%s,conf_file=%s", pin, conf_file)

    cmd_name = ctx.command.name
    __log.debug("cmd_name=%s", cmd_name)

    if not pin:
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
        app = CalibApp(pi, pin, conf_file, debug=debug)
        app.main()

    except (EOFError, KeyboardInterrupt):
        pass

    except Exception as _e:
        __log.error("%s: %s", type(_e).__name__, _e)

    finally:
        if app:
            app.end()
        if pi:
            pi.stop()


@cli.command(help="JSON API Server")
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--server_host", "-s", type=str, default="0.0.0.0", show_default=True,
    help="server hostname or IP address"
)
@click.option(
    "--port", "-p", type=int, default=8000, show_default=True,
    help="port number"
)
@click_common_opts(__version__)
def api_server(ctx, pins, server_host, port, debug):
    """API (JSON) Server ."""
    cmd_name = ctx.command.name

    __log = get_logger(__name__, debug)
    __log.debug("cmd_name=%s", cmd_name)
    __log.debug("pins=%s", pins)
    __log.debug("server_host=%s, port=%s", server_host, port)

    if pins:
        os.environ["PISERVO0_PINS"] = ",".join([str(p) for p in pins])
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
        "piservo0.web.json_api:app",
        host=server_host, port=port, reload=True
    )


@cli.command(help="API Client (JSON)")
@click.argument("cmdline", type=str, nargs=-1)
@click.option(
    "--url", "-u", type=str,
    default="http://localhost:8000/cmd", show_default=True,
    help="API URL"
)
@click.option(
    "--history_file", type=str,
    default="~/.piservo0_apiclient_history", show_default=True,
    help="History file"
)
@click_common_opts(__version__)
def api_client(ctx, cmdline, url, history_file, debug):
    """String API Server."""
    cmd_name = ctx.command.name

    __log = get_logger(__name__, debug)
    __log.debug(
        "cmd_name=%s, url=%s, history_file=%s",
        cmd_name, url, history_file
    )

    # cmdline = " ".join(cmdline)
    __log.debug("cmdline=%a", cmdline)

    _app = CmdApiClient(cmd_name, url, cmdline, history_file, debug)
    try:
        _app.main()

    except (KeyboardInterrupt, EOFError):
        pass

    finally:
        _app.end()


@cli.command(help="String Command API Client")
@click.argument("cmdline", type=str, nargs=-1)
@click.option(
    "--url", "-u", type=str,
    default="http://localhost:8000/cmd", show_default=True,
    help="API URL"
)
@click.option(
    "--history_file", type=str,
    default="~/.piservo0_strclient_history", show_default=True,
    help="History file"
)
@click.option(
    "--angle_factor", "-a", type=str, default="1,1,1,1", show_default=True,
    help="Angle Factor"
)
@click_common_opts(__version__)
def str_client(ctx, cmdline, url, history_file, angle_factor, debug):
    """String Command API Client."""
    cmd_name = ctx.command.name

    __log = get_logger(__name__, debug)
    __log.debug(
        "cmd_name=%s, url=%s, history_file=%s, angle_factor=%s",
        cmd_name, url, history_file, angle_factor
    )
    __log.debug("cmdline=%s", cmdline)

    af_list = [int(i) for i in angle_factor.split(',')]
    __log.debug("af_list=%s", af_list)

    _app = CmdStrClient(cmd_name, url, cmdline, history_file, af_list, debug)
    try:
        _app.main()

    except (KeyboardInterrupt, EOFError):
        pass

    finally:
        _app.end()
