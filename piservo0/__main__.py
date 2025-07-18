#
# (c) 2025 Yoichi Tanibayashi
#
import click
from piservo0 import get_logger
from .cmd_echo import CmdEcho
from .cmd_servo import CmdServo
from .cmd_calib import CmdCalib
from .cmd_multi import CmdMulti


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="""
pyservo0 command
""")
@click.option('-d', '--debug', is_flag=True, help="debug flag")
@click.pass_context
def cli(ctx, debug):
    """ CLI top """
    subcmd = ctx.invoked_subcommand
    log = get_logger(__name__, debug)
    log.debug('subcmd=%s', subcmd)

    if subcmd is None:
        print(f'{ctx.get_help()}')


@cli.command(help="""
echo coomand""")
@click.option('--debug', '-d', is_flag=True, default=False,
              help='debug flag')
def echo(debug):
    """ echo command (just sample command)
    """
    log = get_logger(__name__, debug)
    log.debug('')

    try:
        app = CmdEcho(debug=debug)

    except Exception as _e:
        log.error('%s: %s', type(_e).__name__, _e)
        return

    try:
        app.main()

    except Exception as _e:
        log.warning('%s: %s', type(_e).__name__, _e)

    finally:
        app.end()


@cli.command(help="""
servo command""")
@click.argument('pin', type=int, nargs=1)
@click.argument('pulse', type=str, nargs=1)
@click.option('--sec', '-t', '-s', type=float, default=1.0,
              help='sec')
@click.option('--debug', '-d', is_flag=True, default=False,
              help='debug flag')
def servo(pin, pulse, sec, debug):
    """ servo command
    """
    log = get_logger(__name__, debug)
    log.debug('pin=%s, pulse="%s", sec=%s', pin, pulse, sec)

    try:
        app = CmdServo(pin, pulse, sec, debug=debug)

    except Exception as _e:
        log.error('%s: %s', type(_e).__name__, _e)
        return

    try:
        app.main()

    except Exception as _e:
        log.warning('%s: %s', type(_e).__name__, _e)

    finally:
        app.end()


@cli.command(help="""
calibration tool""")
@click.argument('pin', type=int, nargs=1)
@click.option('--conf_file', '--file', '-c', '-f', type=str,
              default='./servo.json')
@click.option('--sec', '-t', '-s', type=float, default=1,
              help='sec')
@click.option('--debug', '-d', is_flag=True, default=False,
              help='debug flag')
def calib(pin, conf_file, sec, debug):
    """ servo command
    """
    log = get_logger(__name__, debug)
    log.debug('pin=%s,conf_file=%s,sec=%s', pin, conf_file, sec)

    try:
        app = CmdCalib(pin, conf_file, sec, debug=debug)

    except Exception as _e:
        log.error('%s: %s', type(_e).__name__, _e)
        return

    try:
        app.main()

    except Exception as _e:
        log.warning('%s: %s', type(_e).__name__, _e)

    finally:
        app.end()


@cli.command(help="""
multi servo controller""")
@click.argument('pin', type=int, nargs=-1)
@click.option('--conf_file', '--file', '-c', '-f', type=str,
              default='./servo.json')
@click.option('--sec', '-t', '-s', type=float, default=1,
              help='sec')
@click.option('--debug', '-d', is_flag=True, default=False,
              help='debug flag')
def multi(pin, conf_file, sec, debug):
    """ servo command
    """
    log = get_logger(__name__, debug)
    log.debug('pin=%s,conf_file=%s,sec=%s', pin, conf_file, sec)

    try:
        app = CmdMulti(pin, conf_file, sec, debug=debug)

    except Exception as _e:
        log.error('%s: %s', type(_e).__name__, _e)
        return

    try:
        app.main()

    except (EOFError, KeyboardInterrupt) as _e:
        log.debug('%s: %s', type(_e).__name__, _e)

    except Exception as _e:
        log.error('%s: %s', type(_e).__name__, _e)

    finally:
        app.end()
