#
# (c) 2025 Yoichi Tanibayashi
#
# Servo Tool Command
#
import blessed
import click
import pigpio

from piservo0 import MultiServo, get_logger

# clickで、'-h'もヘルプオプションするために
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="Servo Tool",
)
@click.option("-debug", "-d", is_flag=True, help="debug flag")
@click.pass_context
def cli(ctx, debug):
    """CLI top"""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


class CalibApp:
    """
    サーボキャリブレーション用TUIアプリケーション
    """

    SELECTED_SERVO_ALL = -1

    def __init__(self, pins, conf_file, debug=False):
        self._debug = debug
        self._log = get_logger(self.__class__.__name__, self._debug)
        self._log.debug("pins=%s, conf_file=%s", pins, conf_file)

        self.pi = pigpio.pi()
        self.term = blessed.Terminal()
        self.mservo = MultiServo(
            self.pi, pins, conf_file=conf_file, debug=debug
        )

        self.selected_servo = self.SELECTED_SERVO_ALL
        self.running = True

        self.key_bindings = self._setup_key_bindings()

    def _setup_key_bindings(self):
        """キーバインドを設定する"""
        term = self.term
        return {
            # Move
            "w": lambda: self.move_diff(+20),
            "k": lambda: self.move_diff(+20),
            term.KEY_UP: lambda: self.move_diff(+20),
            "s": lambda: self.move_diff(-20),
            "j": lambda: self.move_diff(-20),
            term.KEY_DOWN: lambda: self.move_diff(-20),
            # Fine Tune
            "W": lambda: self.move_diff(+1),
            "K": lambda: self.move_diff(+1),
            "S": lambda: self.move_diff(-1),
            "J": lambda: self.move_diff(-1),
            # Move to angle
            "c": lambda: self.move_angle(0),
            "n": lambda: self.move_angle(-90),
            "v": lambda: self.move_angle(-90),
            "x": lambda: self.move_angle(90),
            # Calibration
            "C": lambda: self.set_calibration("center"),
            "N": lambda: self.set_calibration("min"),
            "V": lambda: self.set_calibration("min"),
            "X": lambda: self.set_calibration("max"),
            # Misc
            "h": self.display_help,
            "?": self.display_help,
            "q": self.quit,
            "Q": self.quit,
        }

    def main(self):
        """メインループ"""
        self._log.debug("starting main loop")
        with self.term.cbreak():
            while self.running:
                self.draw_prompt()
                inkey = self.term.inkey()
                if not inkey:
                    continue

                if inkey.isnumeric():
                    self.select_servo(int(inkey))
                    continue

                action = self.key_bindings.get(inkey)
                if action:
                    action()
                else:
                    print()  # 未知のキー入力の場合は改行

    def draw_prompt(self):
        """プロンプトを表示する"""
        cur_pulse = self.mservo.get_pulse()

        prompt_str = ""
        for i in range(self.mservo.servo_n):
            if i == self.selected_servo:
                prompt_str += "*"
            else:
                prompt_str += " "

            prompt_str += f"[{i + 1}]:{cur_pulse[i]:4} "

        if self.selected_servo < 0:
            prompt_str += "*:ALL"
        else:
            prompt_str += f"{self.selected_servo + 1}:"
            self.selected_pin = self.mservo.pins[self.selected_servo]
            prompt_str += f"GPIO{self.selected_pin}"

        print(f"{prompt_str}> ", end="", flush=True)

    def select_servo(self, num):
        """サーボを選択する"""
        index = num - 1
        if 0 <= index < self.mservo.servo_n:
            self.selected_servo = index
            print(
                f"select {self.selected_servo + 1}:"
                f"GPIO{self.mservo.pins[self.selected_servo]:02d}"
            )
        else:
            self.selected_servo = self.SELECTED_SERVO_ALL
            print("select ALL")
        self._log.debug("selected_servo: %s", self.selected_servo)

    def move_diff(self, diff_pulse):
        """パルス幅を相対的に変更する"""
        cur_pulse = self.mservo.get_pulse()
        if self.selected_servo >= 0:
            dst_pulse = cur_pulse[self.selected_servo] + diff_pulse
            self.mservo.servo[self.selected_servo].move_pulse(
                dst_pulse, forced=True
            )
        else:
            dst_pulse = [p + diff_pulse for p in cur_pulse]
            self.mservo.move_pulse(dst_pulse, forced=True)
        print(f"pulse: {dst_pulse}")

    def move_angle(self, angle):
        """指定角度に移動する"""
        if self.selected_servo >= 0:
            self.mservo.servo[self.selected_servo].move_angle(angle)
        else:
            self.mservo.move_angle_sync([angle] * self.mservo.servo_n, 0.5)
        print(f"angle: {angle}")

    def set_calibration(self, calib_type):
        """キャリブレーション値を設定・保存する"""
        if self.selected_servo < 0:
            print(" Select a servo first.")
            return

        servo = self.mservo.servo[self.selected_servo]
        cur_pulse = servo.get_pulse()

        if calib_type == "center":
            if servo.pulse_min < cur_pulse < servo.pulse_max:
                servo.pulse_center = cur_pulse
            else:
                print(
                    f"\n {cur_pulse}: "
                    + f"out of range:{servo.pulse_min}..{servo.pulse_max}"
                )
                return
        elif calib_type == "min":
            if cur_pulse < servo.pulse_center:
                servo.pulse_min = cur_pulse
            else:
                print(f"\n {cur_pulse}: out of range:..{servo.pulse_center}")
                return
        elif calib_type == "max":
            if cur_pulse > servo.pulse_center:
                servo.pulse_max = cur_pulse
            else:
                print(f"\n {cur_pulse}: out of range: {servo.pulse_center}..")
                return
        else:
            return

        servo.save_conf()
        msg = (
            f"\n GPIO{servo.pin:02d}: {calib_type.capitalize()}"
            f" pulse set to {cur_pulse} and saved."
        )
        print(msg)

    def display_help(self):
        """ヘルプメッセージを表示する"""
        print("""

=== Usage ===
* Select servo
  0: Select All servos
  1..9: Select one servo

* Move
  'w', 'k', UpArrow:   Up
  's', 'j', DownArrow: Down
  (Upper case is for fine tuning)

* Move to angle
  'c': move to center (0 deg)
  'n': move to min (-90 deg)
  'x': move to max (90 deg)

* Calibration
  'C': save current pulse as Center
  'N': save current pulse as Min
  'X': save current pulse as Max

* Misc
  'q': Quit
  'h', '?': Show this help
""")

    def quit(self):
        """アプリケーションを終了する"""
        print(" Quit")
        self.running = False

    def end(self):
        """終了処理"""
        self.mservo.off()
        self.pi.stop()
        print("\n Bye\n")


@cli.command(help="Calibration tool")
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--conf_file", "-c", "-f", default="./servo.json", help="Config file path"
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
def calib(pins, conf_file, debug):
    """Calibrate servo motors"""
    log = get_logger(__name__, debug)
    log.debug("pins=%s, conf_file=%s", pins, conf_file)

    if not pins:
        log.error("No GPIO pins specified.")
        print(
            "Error: Please specify GPIO pins. e.g. `servo_tool calib 17 27`"
        )
        return

    app = CalibApp(pins, conf_file, debug=debug)
    try:
        app.main()
    except KeyboardInterrupt:
        print("\n\n! Keyboard Interrupt")
    except Exception as e:
        log.error("%s: %s", type(e).__name__, e, exc_info=True)
    finally:
        app.end()


if __name__ == "__main__":
    cli()
