#
# (c) 2025 Yoichi Tanibayashi
#
# Servo Tool Command
#
import click
import pigpio
import blessed
from piservo0 import MultiServo, get_logger


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="""
Servo Tool
""")
@click.option('-debug', '-d', is_flag=True, help="debug flag")
@click.pass_context
def cli(ctx, debug):
    """ CLI top """
    
    subcmd = ctx.invoked_subcommand
    log = get_logger(__name__, debug)
    log.debug(f"subcmd={subcmd}")

    if subcmd is None:
        print(f'{ctx.get_help()}')


def move_angle(servo, dst_angle, selected_servo):
    """ """
    if selected_servo >= 0:
        servo.servo[selected_servo].move_angle(dst_angle)
    else:
        dst_angle = [dst_angle] * servo.servo_n
        servo.move_angle(dst_angle)

    cur_pulse = servo.get_pulse()
    print(
        f'servo:{selected_servo}, dst_angle={dst_angle}, cur_pulse={cur_pulse}'
    )


def move_diff(servo, cur_pulse, diff_pulse, selected_servo):
    """  """
    """
    log = get_logger(__name__, True)
    log.debug(f'selected_servo={selected_servo}, cur_pulse={cur_pulse}, diff_pulse={diff_pulse}, selected_servo')
    """

    if selected_servo >= 0:
        dst_pulse = cur_pulse[selected_servo] + diff_pulse
        servo.servo[selected_servo].move_pulse(dst_pulse, forced=True)
    else:
        dst_pulse = [ pulse + diff_pulse for pulse in cur_pulse]
        servo.move_pulse(dst_pulse, forced=True)

    cur_pulse = servo.get_pulse()
    print(
        f'servo:{selected_servo}, dst_pulse={dst_pulse}, cur_pulse={cur_pulse}'
    )


@cli.command(help="""
calibration tool""")
@click.argument('pins', type=int, nargs=-1)
@click.option('--debug', '-d', is_flag=True, default=False, help='debug flag')
def calib(pins, debug):
    """ calibrate servo """

    log = get_logger(__name__, debug)
    log.debug(f'pins={pins}')

    if len(pins) == 0:
        log.error(f'pins={pins}')
        return

    ### init
    term = blessed.Terminal()

    pi = pigpio.pi()
    if not pi.connected:
        log.error('pigpio daemon not connected.')
        return

    servo = MultiServo(pi, pins, debug=debug)

    SELECTED_SERVO_ALL = -1

    try:
        with term.cbreak():
            inkey = ''
            selected_servo = SELECTED_SERVO_ALL

            while inkey.lower() != 'q':
                cur_pulse = servo.get_pulse()

                print(f'{selected_servo+1:>3}> ', end='', flush=True)
                inkey = term.inkey()
                if not inkey:
                    continue

                if inkey in '0123456789':
                    selected_servo = int(inkey) - 1
                    log.debug(f'servo:{selected_servo}')

                    if selected_servo >= servo.servo_n:
                        log.warning(f'servo:{selected_servo}: out of range')
                        selected_servo = SELECTED_SERVO_ALL

                    print(f'select servo: {selected_servo + 1} (0=all), {cur_pulse}')
                    continue

                if inkey in ('w', 'k', term.KEY_LEFT):
                    move_diff(servo, cur_pulse, +20, selected_servo)
                    continue

                if inkey in 'WK':
                    move_diff(servo, cur_pulse, -1, selected_servo)
                    continue

                if inkey in ('s', 'j', term.KEY_RIGHT):
                    move_diff(servo, cur_pulse, -20, selected_servo)
                    continue

                if inkey in 'SJ':
                    move_diff(servo, cur_pulse, +1, selected_servo)
                    continue

                if inkey in 'c':
                    move_angle(servo, 0, selected_servo)
                    continue

                if inkey in 'n':
                    move_angle(servo, -90, selected_servo)
                    continue

                if inkey in 'x':
                    move_angle(servo, +90, selected_servo)
                    continue


                if inkey in 'qQ':
                    print('Quit')
                    break

                print()
                continue

    except KeyboardInterrupt as e:
        log.info(f'{type(e).__name__}')

    finally:
        servo.off()
        pi.stop()
        print('\n Bye\n')


if __name__ == '__main__':
    cli()
