#
# (c) 2025 Yoichi Tanibayashi
#
import pprint

import blessed

from piservo0 import CalibrableServo, get_logger


class CalibApp:
    """CalibApp:サーボキャリブレーション用CUIアプリケーション."""

    TARGET_CENTER = 0
    TARGET_MIN = -90
    TARGET_MAX = 90
    TARGETS = [TARGET_MIN, TARGET_CENTER, TARGET_MAX]

    def __init__(self, pi, pin, conf_file, debug=False):
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("pin=%s, conf_file=%s", pin, conf_file)

        self.pi = pi
        self.pin = pin
        self.conf_file = conf_file
        
        if not self.pi.connected:
            raise ConnectionError("pigpio daemon not connected.")

        self.cur_target = self.TARGET_CENTER
        self.__log.debug("cur_target=%s", self.cur_target)

        self.term = blessed.Terminal()
        self.servo = CalibrableServo(
            self.pi, self.pin, conf_file=self.conf_file, debug=self._debug
        )
        self.conf_file = self.servo.conf_file
        self.__log.debug("conf_file=%s", self.conf_file)

        self.servo.move_center()

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
            # Change target
            "KEY_TAB": self.inc_target,
            "KEY_BTAB": self.dec_target,
            # Move to angle
            "c": lambda: self.set_target(self.TARGET_CENTER),
            "n": lambda: self.set_target(self.TARGET_MIN),
            "v": lambda: self.set_target(self.TARGET_MIN),
            "x": lambda: self.set_target(self.TARGET_MAX),
            # Move
            "w": lambda: self.move_diff(+20),
            "s": lambda: self.move_diff(-20),
            "k": lambda: self.move_diff(+20), #  vi like
            "j": lambda: self.move_diff(-20), #  vi like
            "KEY_UP": lambda: self.move_diff(+20),
            "KEY_DOWN": lambda: self.move_diff(-20),
            # Fine Tune
            "W": lambda: self.move_diff(+1),
            "S": lambda: self.move_diff(-1),
            "K": lambda: self.move_diff(+1),
            "J": lambda: self.move_diff(-1),
            # Calibration
            "KEY_ENTER": lambda: self.set_calibration(),
            " ": lambda: self.set_calibration(),
            # Misc
            "h": self.display_help,
            "H": self.display_help,
            "?": self.display_help,
            "q": self.quit,
            "Q": self.quit,
        }

    def main(self):
        """メインループ"""
        print("\nCalibration Tool: 'h' for help, 'q' for quit")
        self.show()

        self.__log.debug("starting main loop")
        with self.term.cbreak():
            while self.running:
                self.print_prompt()
                inkey = self.term.inkey()
                if not inkey:
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

    def show(self):
        """Show current setup."""
        print()
        print(f"* conf_file: {self.conf_file}")
        print()
        print(f"* GPIO{self.pin}")
        print(f"   -90 deg: pulse = {self.servo.pulse_min:-4d}")
        print(f"     0 deg: pulse = {self.servo.pulse_center:-4d}")
        print(f"    90 deg: pulse = {self.servo.pulse_max:-4d}")
        print()

    def print_prompt(self):
        """Print Prompt string."""
        _cur_pulse = self.servo.get_pulse()
        
        prompt_str = (
            f"GPIO{self.pin}"
            ": "
            f"{self.cur_target} deg"
            ": "
            f"pulse={_cur_pulse}"
        )

        print(f"{prompt_str}> ", end="", flush=True)

    def inc_target(self):
        """Change target ciclick."""

        _idx = self.TARGETS.index(self.cur_target)
        _idx = (_idx + 1) % len(self.TARGETS)

        self.set_target(self.TARGETS[_idx])

    def dec_target(self):
        """Change target ciclick."""

        _idx = self.TARGETS.index(self.cur_target)
        _idx = (_idx - 1) % len(self.TARGETS)

        self.set_target(self.TARGETS[_idx])

    def set_target(self, target: int):
        """Set target."""

        if target in self.TARGETS:
            self.cur_target = target
            self.__log.debug("cur_target=%s", self.cur_target)
            print(f"target={self.cur_target} deg")
            self.servo.move_angle(self.cur_target)
        
    def move_diff(self, diff_pulse):
        """パルス幅を相対的に変更する"""

        # 現在のパルス値を取得
        cur_pulse = self.servo.get_pulse()

        # 移動先パルス値の算出
        dst_pulse = cur_pulse + diff_pulse
        dst_pulse = max(min(dst_pulse, self.servo.MAX), self.servo.MIN)
        self.__log.debug("dst_pulse=%s", dst_pulse)

        # サーボを動かす
        self.servo.move_pulse(dst_pulse, forced=True)

        print(f"pulse:{dst_pulse}")

    def set_calibration(self):
        """キャリブレーション値を設定・保存する"""

        cur_pulse = self.servo.get_pulse()

        if self.cur_target == self.TARGET_CENTER:
            if self.servo.pulse_min < cur_pulse < self.servo.pulse_max:
                self.servo.pulse_center = cur_pulse
            else:
                print()
                self.__log.warning(
                    "%s: out of range:%s..%s",
                    cur_pulse, self.servo.pulse_min, self.servo.pulse_max
                )
                return
        elif self.cur_target == self.TARGET_MIN:
            if self.servo.MIN <= cur_pulse < self.servo.pulse_center:
                self.servo.pulse_min = cur_pulse
            else:
                print()
                self.__log.warning(
                    "%s: out of range:%s..%s",
                    cur_pulse, self.servo.MIN, self.servo.pulse_center
                )
                return
        elif self.cur_target == self.TARGET_MAX:
            if self.servo.pulse_center < cur_pulse <= self.servo.MAX:
                self.servo.pulse_max = cur_pulse
            else:
                print()
                self.__log.warning(
                    "%s: out of range:%s..%s",
                    cur_pulse, self.servo.pulse_center, self.servo.MAX
                )
                return
        else:
            self.__log.warning("cur_target=%s??", self.cur_target)
            return

        _msg1 = f"Save! GPIO{self.pin}"
        _msg2 = f"{self.cur_target} deg"
        _msg3 = f"pulse={cur_pulse}"
        print(_msg1, ": ", _msg2, ": ", _msg3)

    def display_help(self):
        """ヘルプメッセージを表示する"""
        print(
            """=== Usage ===
            
* Select target (Cyclic):
            
 -90 deg ------[TAB]-----> 0 deg ------[TAB]-----> 90 deg
 -90 deg <-[Shift]+[TAB]-- 0 deg <-[Shift]+[TAB]-- 90 deg

* Move: (Upper case is for fine tuning)

        [w], [Up] ,[k]
              ^
              v
        [s],[Down],[j]   

* Save: [ENTER],[SPACE] : save current pulse

* Misc: [q], [Q] : Quit
        [h], [?] : Show this help"""
        )
        self.show()

    def quit(self):
        """アプリケーションを終了する"""
        print("=== Quit ===")
        self.running = False

    def end(self):
        """終了処理"""
        self.servo.off()
        self.show()
