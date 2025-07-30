#
# (c) 2025 Yoichi Tanibayashi
#
""" piservo.py """
from ..utils.my_logger import get_logger


class PiServo:
    """Raspberry PiのGPIOピンを介してサーボモーターを制御するクラス。

    pigpioライブラリを使用して、サーボモーターのパルス幅を設定し、
    位置を制御する。

    Attributes:
        OFF (int): サーボをオフにするパルス幅（0）。
        MIN (int): 最小パルス幅（500マイクロ秒）。
        MAX (int): 最大パルス幅（2500マイクロ秒）。
        CENTER (int): 中央位置のパルス幅（1500マイクロ秒）。
    """

    OFF = 0
    MIN = 500
    MAX = 2500
    CENTER = 1500

    def __init__(self, pi, pin, debug=False):
        """PiServoクラスのコンストラクタ。

        Args:
            pi (pigpio.pi):
                pigpio.piのインスタンス。サーボモーターを制御するために必要。
            pin (int, optional):
                サーボモーターが接続されているGPIOピン番号。
            debug (bool, optional):
                デバッグログを有効にするかどうかのフラグ。
                Trueの場合、詳細なログが出力される。デフォルトはFalse。
        """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("pin=%s", pin)

        self.pi = pi
        self.pin = pin

    def get_pulse(self):
        """現在のサーボモーターのパルス幅を取得する。

        Returns:
            int: 現在のパルス幅 (マイクロ秒)。
        """
        pulse = self.pi.get_servo_pulsewidth(self.pin)
        self.__log.debug("pulse=%s", pulse)

        return pulse

    def move_pulse(self, pulse):
        """サーボモーターを指定されたパルス幅に移動させる。

        パルス幅はMINからMAXの範囲に制限される。
        指定されたパルス幅が範囲外の場合、自動的に最小値または最大値に調整される。

        Args:
            pulse (int):
                サーボモーターに設定するパルス幅（マイクロ秒）。
                この値に基づいてサーボの位置が決定される。
        """
        self.__log.debug("pin=%s, pulse=%s", self.pin, pulse)

        if pulse < self.MIN:
            self.__log.warning(f"{pulse} < MIN({self.MIN})")
            pulse = self.MIN

        if pulse > self.MAX:
            self.__log.warning(f"{pulse} > MAX({self.MAX})")
            pulse = self.MAX

        self.pi.set_servo_pulsewidth(self.pin, pulse)

    def move_min(self):
        """サーボモーターを最小位置に移動させる。

        パルス幅をMINに設定する。
        """
        self.__log.debug(f"pin={self.pin}")

        self.move_pulse(self.MIN)

    def move_max(self):
        """サーボモーターを最大位置に移動させる。

        パルス幅をMAXに設定する。
        """
        self.__log.debug(f"pin={self.pin}")

        self.move_pulse(self.MAX)

    def move_center(self):
        """サーボモーターを中央位置に移動させる。

        パルス幅をCENTERに設定する。
        """
        self.__log.debug(f"pin={self.pin}")

        self.move_pulse(self.CENTER)

    def off(self):
        """サーボモーターの電源をオフにする。

        サーボモーターのパルス幅をOFF (0) に設定し、動作を停止させる。
        """
        self.__log.debug(f"pin={self.pin}")

        self.pi.set_servo_pulsewidth(self.pin, self.OFF)
