#
# (c) 2025 Yoichi Tanibayashi
#
import pprint

import blessed

from piservo0 import MultiServo, PiServo, get_logger


class CalibApp:
    """
    サーボキャリブレーション用TUIアプリケーション
    """

    SELECTED_SERVO_ALL = -1

    def __init__(self, pi, pins, conf_file, debug=False):
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("pins=%s, conf_file=%s", pins, conf_file)

        if not pi.connected:
            raise ConnectionError("pigpio daemon not connected.")

        self.term = blessed.Terminal()
        self.mservo = MultiServo(pi, pins, conf_file=conf_file, debug=debug)

        self.selected_servo = self.SELECTED_SERVO_ALL
        self.running = True

        self.key_bindings = self._setup_key_bindings()
        self.__log.debug(
            "key_bindings=%s",
            pprint.pformat(self.key_bindings, indent=2)
            .replace("{", "{\n ")
            .replace("}", "\n}"),
        )

    def _setup_key_bindings(self):
        """キーバインドを設定する

        **補足**: メソッドとして独立させる理由
        - __init__()内で直接代入するよりは、分けたほうが「美しい」。
        - selfメソッドを割り当てるため、クラス変数にはできない。
        - 引数が必要なメソッドを割り当てる場合 `lambda:`にする必要がある。
        """
        return {
            # Move
            "w": lambda: self.move_diff(+20),
            "k": lambda: self.move_diff(+20),
            "KEY_UP": lambda: self.move_diff(+20),
            "s": lambda: self.move_diff(-20),
            "j": lambda: self.move_diff(-20),
            "KEY_DOWN": lambda: self.move_diff(-20),
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
        print("\nCalibration Tool: 'h' for help, 'q' for quit\n")
        print(f"  conf_file = {self.mservo.conf_file}\n")

        self.__log.debug("starting main loop")
        with self.term.cbreak():
            while self.running:
                self.draw_prompt()
                inkey = self.term.inkey()
                if not inkey:
                    continue

                if inkey.isnumeric():
                    self.select_servo(int(inkey))
                    continue

                if inkey.is_sequence:
                    _inkey = inkey.name
                else:
                    _inkey = str(inkey)
                self.__log.debug("_inkey=%s", _inkey)

                if _inkey:
                    action = self.key_bindings.get(_inkey)

                    if action:
                        action()
                        continue

                print(f"'{_inkey}': unknown key")

    def draw_prompt(self):
        """プロンプトを表示する"""
        prompt_str = ""
        for i in range(self.mservo.servo_n):
            if i == self.selected_servo:
                prompt_str += "*"
            else:
                prompt_str += " "

            prompt_str += f"{i + 1}:pin{self.mservo.pins[i]} "

        if self.selected_servo < 0:
            prompt_str += "| _:ALL"
        else:
            prompt_str += f"| {self.selected_servo + 1}:"
            _selected_pin = self.mservo.pins[self.selected_servo]
            prompt_str += f"pin{_selected_pin}"

        print(f"{prompt_str}> ", end="", flush=True)

    def select_servo(self, num):
        """サーボを選択する"""
        index = num - 1
        if 0 <= index < self.mservo.servo_n:
            self.selected_servo = index
            print(
                f"select {self.selected_servo + 1}:"
                f"pin{self.mservo.pins[self.selected_servo]:02d}"
            )
        else:
            self.selected_servo = self.SELECTED_SERVO_ALL
            print("select ALL")
        self.__log.debug("selected_servo: %s", self.selected_servo)

    def move_diff(self, diff_pulse):
        """パルス幅を相対的に変更する"""
        cur_pulse = self.mservo.get_pulse()

        if self.selected_servo >= 0:
            dst_pulse = cur_pulse[self.selected_servo] + diff_pulse
            dst_pulse = max(min(dst_pulse, PiServo.MAX), PiServo.MIN)
            self.__log.debug("dst_pulse=%s", dst_pulse)
            self.mservo.servo[self.selected_servo].move_pulse(dst_pulse, forced=True)
        else:  # ALL
            dst_pulse = [
                max(min(p + diff_pulse, PiServo.MAX), PiServo.MIN) for p in cur_pulse
            ]
            self.__log.debug("dst_pulse=%s", dst_pulse)
            self.mservo.move_pulse(dst_pulse, forced=True)

        print(f"pulse:{dst_pulse}")

    def move_angle(self, angle):
        """指定角度に移動する"""
        self.__log.debug("angle=%s", angle)

        if self.selected_servo >= 0:
            self.mservo.servo[self.selected_servo].move_angle(angle)
            _pulse = self.mservo.get_pulse()
            print(f"angle: {angle}, pulse: {_pulse[self.selected_servo]}")
        else:
            self.mservo.move_angle_sync([angle] * self.mservo.servo_n, 0.5)
            print(f"angle: {angle}, pulse: {self.mservo.get_pulse()}")

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
        print(
            """

=== Usage ===
* Select servo
  0: Select All servos
  1..9: Select one servo

* Move
    'w',  UpArrow, 'k'
             ^
             |
             v
    's', DownArrow, 'j'

  'w', 'k', UpArrow   : Up
  's', 'j', DownArrow : Down
  (Upper case is for fine tuning)

* Move to angle
       MIN    CENTER    MAX
    'n','v' <-- 'c' --> 'x'

  'c'      : move to center (0 deg)
  'n', 'v' : move to min (-90 deg)
  'x'      : move to max (90 deg)

* Calibration
  'C'      : save current pulse as Center
  'N', 'V' : save current pulse as Min
  'X'      : save current pulse as Max

* Misc
  'q', 'Q' : Quit
  'h', '?' : Show this help
"""
        )

    def quit(self):
        """アプリケーションを終了する"""
        print(" Quit")
        self.running = False

    def end(self):
        """終了処理"""
        self.mservo.off()
        print("\n Bye\n")
