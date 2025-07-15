#
# (c) 2025 Yoichi Tanibayashi
#
import time
import click
import pigpio
from piservo0 import PiServo
from piservo0 import CalibrableServo
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
@click.option('--sec', '-t', '-s', type=float, default=1,
    help='sec')
@click.option('--debug', '-d', is_flag=True, default=False,
    help='debug flag')
def servo(pin, pulse, sec, debug):
    """ servo command
    """
    log = get_logger(__name__, debug)
    log.debug(f'pin={pin}, pulse="{pulse}", sec={sec}')

    pi = pigpio.pi()
    if not pi.connected:
        log.error('pigpio daemon not connected.')
        return

    servo = PiServo(pi, pin, debug=debug)

    try:
        try:
            pulse_int = int(pulse)
        except ValueError:

            if pulse == "min":
                pulse_int = PiServo.MIN
            elif pulse == "max":
                pulse_int = PiServo.MAX
            elif pulse == "center":
                pulse_int = PiServo.CENTER
            else:
                log.warning(f'"{pulse}": invalid pulse string')
                pulse_int = -1

            log.debug(f'pulse_int={pulse_int}')
            
        if PiServo.MIN <= pulse_int <= PiServo.MAX:
            servo.move(pulse_int)
            time.sleep(sec)
        else:
            log.error(f'pulse_int={pulse_int}: invalid value. do nothing')

    finally:
        log.debug('finally')
        servo.off()
        pi.stop()


@cli.command(help="""
calibration command""")
@click.argument('pin', type=int, nargs=1)
@click.option('--sec', '-t', '-s', type=float, default=1,
    help='sec')
@click.option('--debug', '-d', is_flag=True, default=False,
    help='debug flag')
def cservo(pin, sec, debug):
    """ servo command
    """
    log = get_logger(__name__, debug)
    log.debug(f'pin={pin}, sec={sec}')

    pi = pigpio.pi()
    if not pi.connected:
        log.error('pigpio daemon not connected.')
        return

    try:
        servo = CalibrableServo(pi, pin, debug=debug)
    except Exception as e:
        log.error(f'type(e).__name__: {e}')
        pi.stop()
        return

    try:
        while True:
            in_str = input('> ')
            log.debug(f'in_str={in_str}')

            # 数値が入力されたか？
            try:
                val = float(in_str)

                # 角度として入力されたか？
                if CalibrableServo.ANGLE_MIN <= val <= CalibrableServo.ANGLE_MAX:
                    servo.move_angle(val)
                    pulse = servo.get_pulse()
                    print(f'angle = {val}, pulse={pulse}')
                    time.sleep(sec)
                    continue

                # パルス幅として入力されたか？
                if PiServo.MIN <= val <= PiServo.MAX:
                    servo.move(int(round(val)), forced=True)
                    pulse = servo.get_pulse()
                    print(f'pulse = {pulse}')
                    time.sleep(sec)
                    continue

                log.error(f'{val}: out of range')
                continue

            except ValueError:
                # 文字列が入力された
                pass

            if in_str in ('c', 'center'):
                servo.move_center()
                pulse = servo.get_pulse()
                print(f'center: pulse={pulse}')
                time.sleep(sec)
                continue

            if in_str in ('n', 'min'):
                servo.move_min()
                pulse = servo.get_pulse()
                print(f'min: pulse={pulse}')
                time.sleep(sec)
                continue

            if in_str in ('x', 'max'):
                servo.move_max()
                pulse = servo.get_pulse()
                print(f'max: pulse={pulse}')
                time.sleep(sec)
                continue

            if in_str in ('g', 'get'):
                pulse = servo.get_pulse()
                print(f'pulse = {pulse}')
                continue

            if in_str in ('sc', 'set center'):
                pulse = servo.get_pulse()
                servo.set_center(pulse)
                print(f'set center: pulse = {pulse}')
                continue

            if in_str in ('sn', 'set min'):
                pulse = servo.get_pulse()
                servo.set_min(pulse)
                print(f'set min: pulse = {pulse}')
                continue

            if in_str in ('sx', 'set max'):
                pulse = servo.get_pulse()
                servo.set_max(pulse)
                print(f'set max: pulse = {pulse}')
                continue

            log.error(f'{in_str}: invalid command')

    except (EOFError, KeyboardInterrupt):
        print('\nBye!')

    finally:
        servo.off()
        pi.stop()
