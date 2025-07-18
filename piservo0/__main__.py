#
# (c) 2025 Yoichi Tanibayashi
#
import time
import click
import pigpio
from piservo0 import PiServo
from piservo0 import CalibrableServo
from piservo0 import MultiServo
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
    log.debug('subcmd=%s', subcmd)

    if subcmd is None:
        print(f'{ctx.get_help()}')


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
            servo.move_pulse(pulse_int)
            time.sleep(sec)
        else:
            log.error(f'pulse_int={pulse_int}: invalid value. do nothing')

    finally:
        log.debug('finally')
        servo.off()
        pi.stop()


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
    ctx = click.get_current_context()
    cmd_name = ctx.command.name

    PROMPT_STR = f'\n{cmd_name}: [h] for help, [q] for exit > '

    log = get_logger(__name__, debug)
    log.debug('pin=%s,conf_file=%s,sec=%s', pin, conf_file, sec)

    CMD_CENTER = {'help': 'move center', 'str': ('center', 'c')}
    CMD_ANGLE = {'help': 'move angle', 'str': '-90.0 .. 0.0 .. 90.0'}
    CMD_PULSE = {'help': 'move pulse', 'str': '500 .. 2500'}
    CMD_MIN = {'help': 'move min', 'str': ('min', 'n')}
    CMD_MAX = {'help': 'move max', 'str': ('max', 'x')}
    CMD_GET = {'help': 'get pulse', 'str': ('get pulse', 'get', 'g')}
    CMD_SET_CENTER = {'help': 'set center', 'str': ('set center', 'sc')}
    CMD_SET_MIN = {'help': 'set min', 'str': ('set min', 'sn')}
    CMD_SET_MAX = {'help': 'set max', 'str': ('set max', 'sx')}
    CMD_EXIT = {'help': 'exit', 'str': ('exit', 'quit', 'q', 'bye')}
    CMD_HELP = {'help': 'help', 'str': ('help', 'h', '?')}

    CMDS = [
        CMD_ANGLE, CMD_PULSE,
        CMD_CENTER, CMD_MIN, CMD_MAX,
        CMD_GET,
        CMD_SET_CENTER, CMD_SET_MIN, CMD_SET_MAX,
        CMD_HELP,
        CMD_EXIT
    ]

    pi = pigpio.pi()
    if not pi.connected:
        log.error('pigpio daemon not connected.')
        return

    try:
        servo = CalibrableServo(pi, pin, conf_file=conf_file,
                                debug=debug)
    except Exception as _e:
        log.error('%s: %s', type(_e).__name__, _e)
        pi.stop()
        return

    print(f'[[ "{cmd_name}": Servo Calibration Tool ]]')
    print(f' GPIO: {servo.pin}')
    print(f' conf_file: {servo.conf_file}')

    angle_min = CalibrableServo.ANGLE_MIN
    angle_max = CalibrableServo.ANGLE_MAX
    pulse_min = PiServo.MIN
    pulse_max = PiServo.MAX

    try:
        while True:
            in_str = input(PROMPT_STR)
            log.debug('in_str=%s', in_str)

            # 数値が入力されたか？
            try:
                val = float(in_str)

                # 角度として入力されたか？
                if angle_min <= val <= angle_max:
                    servo.move_angle(val)
                    pulse = servo.get_pulse()
                    print(f' angle = {val}, pulse={pulse}')
                    time.sleep(sec)
                    continue

                # パルス幅として入力されたか？
                if pulse_min <= val <= pulse_max:
                    servo.move_pulse(int(round(val)), forced=True)
                    pulse = servo.get_pulse()
                    print(f' pulse = {pulse}')
                    time.sleep(sec)
                    continue

                log.error('%s: out of range', val)
                continue

            except ValueError:
                # 文字列が入力された
                pass

            if in_str in CMD_HELP['str']:
                print('\nUSAGE\n')

                for cmd in CMDS:
                    cmds = ''
                    if type(cmd['str']) is str:
                        cmds = cmd['str']
                    else:
                        for s in cmd['str']:
                            cmds += f'"{s}", '
                        cmds = cmds[:-2]
                    print(f' {cmds:28} {cmd["help"]:12}')

                continue

            if in_str in CMD_CENTER['str']:
                servo.move_center()
                pulse = servo.get_pulse()
                print(f' center: pulse={pulse}')
                time.sleep(sec)
                continue

            if in_str in CMD_MIN['str']:
                servo.move_min()
                pulse = servo.get_pulse()
                print(f' min: pulse={pulse}')
                time.sleep(sec)
                continue

            if in_str in CMD_MAX['str']:
                servo.move_max()
                pulse = servo.get_pulse()
                print(f' max: pulse={pulse}')
                time.sleep(sec)
                continue

            if in_str in CMD_GET['str']:
                pulse = servo.get_pulse()
                print(f' pulse = {pulse}')
                continue

            if in_str in CMD_SET_CENTER['str']:
                pulse = servo.get_pulse()
                servo.set_center(pulse)
                print(f' set center: pulse = {pulse}')
                print(f' file: {servo.conf_file}')
                continue

            if in_str in CMD_SET_MIN['str']:
                pulse = servo.get_pulse()
                servo.set_min(pulse)
                print(f' set min: pulse = {pulse}')
                print(f' file: {servo.conf_file}')
                continue

            if in_str in CMD_SET_MAX['str']:
                pulse = servo.get_pulse()
                servo.set_max(pulse)
                print(f' set max: pulse = {pulse}')
                print(f' file: {servo.conf_file}')
                continue

            if in_str in CMD_EXIT['str']:
                break

            log.error('%s: invalid command', in_str)

    except (EOFError, KeyboardInterrupt) as _e:
        log.debug('%s: %s', type(_e).__name__, _e)

    finally:
        print('\n Bye!\n')
        servo.off()
        pi.stop()


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
    ctx = click.get_current_context()
    cmd_name = ctx.command.name

    prompt_str = f'\n{cmd_name}: [q] for exit > '

    CMD_EXIT = ('exit', 'quit', 'q', 'bye')

    log = get_logger(__name__, debug)
    log.debug('pin=%s,conf_file=%s,sec=%s', pin, conf_file, sec)

    pi = pigpio.pi()
    if not pi.connected:
        log.error('pigpio daemon not connected.')
        return

    try:
        servo = MultiServo(pi, pin, conf_file, debug=debug)
    except Exception as _e:
        log.error('%s: %s', type(_e).__name__, _e)
        pi.stop()
        return

    print(f'[[ "{cmd_name}": Multipule Servo Motors Controller ]]')
    print(f' GPIO: {servo.pins}')
    print(f' conf_file: {servo.conf_file}')
    try:
        while True:
            in_str = input(prompt_str)
            log.debug('in_str="%s"', in_str)

            if in_str in CMD_EXIT:
                break

            words = in_str.split()
            log.debug('words=%s', words)

            try:
                angles = [float(word) for word in words]
                log.debug('angles=%s', angles)

                time_start = time.time()
                servo.move_angle_sync(angles, sec)
                time_end = time.time()

                elapsed_time = time_end - time_start
                moved_angles = servo.get_angle()
                angles_str = ", ".join(
                    [f"{p:.0f}" for p in moved_angles]
                )
                angles_str = '[' + angles_str + ']'
                print(f' {angles_str} ... {elapsed_time:.3f} sec')

            except ValueError as _e:
                log.error('%s: %s', type(_e).__name__, _e)

    except (EOFError, KeyboardInterrupt) as _e:
        log.debug('%s: %s', type(_e).__name__, _e)

    except Exception as _e:
        log.error('%s: %s', type(_e).__name__, _e)

    finally:
        print('\n Bye!\n')
        servo.off()
        pi.stop()
