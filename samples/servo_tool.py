#
# (c) 2025 Yoichi Tanibayashi
#
# Servo Tool Command
#
import click
import pigpio
import blessed
from piservo0 import MultiServo, get_logger


# clickで、'-h'もヘルプオプションするために
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


class CalibApp:
    """ """
    SELECTED_SERVO_ALL = -1

    def __init__(self, pins, conf_file, debug=False):
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('pins=%s', pins)

        self.pins = pins
        self.conf_file = conf_file

        self.pi = pigpio.pi()
        self.term = blessed.Terminal()

        self.mservo = MultiServo(self.pi, pins,
                                 conf_file=self.conf_file,
                                 debug=debug)

    def main(self):
        """ """
        self._log.debug('')

        with self.term.cbreak():
            inkey = ''
            selected_servo = self.SELECTED_SERVO_ALL

            while inkey.lower() != 'q':
                cur_pulse = self.mservo.get_pulse()

                if selected_servo >= 0:
                    gpio_str = f'{selected_servo + 1}:'
                    gpio_str += f'GPIO{self.pins[selected_servo]:02d}'
                else:
                    gpio_str = '-:ALL'

                # 配列内の要素をフォーマットするトリッキーなやり方
                str_list = [f"{item:4}" for item in cur_pulse]
                print(f'[{", ".join(str_list)}] {gpio_str}> ',
                      end='', flush=True)

                inkey = self.term.inkey()
                if not inkey:
                    continue

                if inkey in '0123456789':
                    # サーボの選択
                    selected_servo = int(inkey) - 1
                    self._log.debug(f'servo:{selected_servo}')

                    print('select ', end='')
                    if selected_servo >= self.mservo.servo_n:
                        selected_servo = self.SELECTED_SERVO_ALL
                        print('ALL')
                    else:
                        print(f'{selected_servo + 1}:' +
                              f'GPIO{self.pins[selected_servo]:02d}')
                    continue

                if inkey in ('w', 'k', self.term.KEY_LEFT):
                    self.move_diff(self.mservo, cur_pulse, +20,
                                   selected_servo)
                    continue

                if inkey in 'WK':
                    self.move_diff(self.mservo, cur_pulse, -1,
                                   selected_servo)
                    continue

                if inkey in ('s', 'j', self.term.KEY_RIGHT):
                    self.move_diff(self.mservo, cur_pulse, -20,
                                   selected_servo)
                    continue

                if inkey in 'SJ':
                    self.move_diff(self.mservo, cur_pulse, +1,
                                   selected_servo)
                    continue

                if inkey in 'c':
                    self.move_angle(self.mservo, 0, selected_servo)
                    continue

                if inkey in 'n':
                    self.move_angle(self.mservo, -90, selected_servo)
                    continue

                if inkey in 'x':
                    self.move_angle(self.mservo, +90, selected_servo)
                    continue

                if inkey in 'C':
                    self.set_centerJ()
                    continue

                if inkey in 'N':
                    self.set_min()
                    continue

                if inkey in 'X':
                    self.set_max()
                    continue

                if inkey in 'hH?':
                    self.help()
                    continue

                if inkey in 'qQ':
                    print(' Quit')
                    break

                print()
                continue

    def end(self):
        """  """
        self._log.debug('')

        self.mservo.off()
        self.pi.stop()
        print('\n Bye\n')

    def set_center(self):
        pass

    def set_min(self):
        pass

    def set_max(self):
        pass

    def help(self):
        """  """
        self._log.debug('')

        print('''

=== Usage ===

* Select servo
  0: Select All servos
  1 .. 9: Select one servo

* Move
  'w', 'k': Up
  's', 'j': Down
  Upper case('W','K','S','J'): Fine Tuning

  (Lower case)
  'c': move center <-- [c]enter
  'n': move min    <-- mi[n]
  'x': move max    <-- ma[x]

* Calibration (ToDo)
  (Upper case)
  'C': save center <-- [C]enter
  'N': save min    <-- mi[N]
  'X': save max    <-- ma[X]

* etc.
  'q': Quit
  'h': Help (This usage)
''')

    def move_angle(self, servo, dst_angle, selected_servo):
        """ """
        if selected_servo >= 0:
            servo.servo[selected_servo].move_angle(dst_angle)
        else:
            dst_angle = [dst_angle] * servo.servo_n
            servo.move_angle(dst_angle)

        print('servo:%s, dst_angle=%s' % (selected_servo, dst_angle))

    def move_diff(self, servo, cur_pulse, diff_pulse, selected_servo):
        """  """
        self._log.debug(
            'selected_servo=%s,' +
            'cur_pulse=%s, ' +
            'diff_pulse=%s, selected_servo',
            selected_servo, cur_pulse, diff_pulse
        )

        if selected_servo >= 0:
            dst_pulse = cur_pulse[selected_servo] + diff_pulse
            servo.servo[selected_servo].move_pulse(dst_pulse, forced=True)
        else:
            dst_pulse = [pulse + diff_pulse for pulse in cur_pulse]
            servo.move_pulse(dst_pulse, forced=True)

        print('servo:%s, dst_pulse=%s' % (selected_servo, dst_pulse))


@cli.command(help="""
calibration tool""")
@click.argument('pins', type=int, nargs=-1)
@click.option('--conf_file', '-c', '-f', default='./servo.json',
              help='config file')
@click.option('--debug', '-d', is_flag=True, default=False,
              help='debug flag')
def calib(pins, conf_file, debug):
    """ calibrate servo """

    log = get_logger(__name__, debug)
    log.debug('pins=%s, conf_file=%s', pins, conf_file)

    if len(pins) == 0:
        log.error(f'pins={pins}')
        return

    app = CalibApp(pins, conf_file, debug=debug)

    try:
        app.main()

    except KeyboardInterrupt:
        print('\n\n! Keyboard Interrupt')

    except Exception as e:
        log.error('%s: %s', type(e).__name__, e)

    finally:
        app.end()


if __name__ == '__main__':
    cli()
