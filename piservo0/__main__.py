#
# (c) 2025 Yoichi Tanibayashi
#
import time
import click
import pigpio
from piservo0 import PiServo
from piservo0 import get_logger


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
    log.debug(f"subcmd={subcmd}")

    if subcmd is None:
        print(f'{ctx.get_help()}')


@cli.command(help="""
servo command""")
@click.argument('pin', type=int, nargs=1)
@click.argument('pulse', type=str, nargs=1)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
    help='debug flag')
def servo(pin, pulse, debug):
    """ servo command
    """
    log = get_logger(__name__, debug)
    log.debug(f'pin={pin}, pulse={pulse}')

    pi = pigpio.pi()

    servo = PiServo(pi, pin, debug)

    try:
        pulse_int = int(pulse)
    except ValueError as e:
        log.debug(f'"{pulse}": {e}')

        if pulse == "min":
            pulse_int = PiServo.MIN
        elif pulse == "max":
            pulse_int = PiServo.MAX
        elif pulse == "center":
            pulse_int = PiServo.CENTER
        else:
            pulse_int = -1

        log.debug(f'pulse_int={pulse_int}')
            
    if pulse_int >= 0:
        servo.move(pulse_int)
        time.sleep(1)

    servo.off()
