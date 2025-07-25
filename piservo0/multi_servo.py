#
# (c) 2025 Yoichi Tanibayashi
#
import time

from .calibrable_servo import CalibrableServo
from .my_logger import get_logger


class MultiServo:
    """
    複数のサーボモーターを制御する。
    """

    DEF_ESTIMATED_TIME = 0.2  # sec
    DEF_STEP_N = 40

    def __init__(
        self, pi, pins: list[int], first_move=True,
        conf_file=CalibrableServo.DEF_CONF_FILE,
        debug=False
    ):
        """
        MultiServoのインスタンスを初期化する。

        Parameters
        ----------
        pi: pigpio.pi
            pigpio.piのインスタンス。
        pins: list[int]
            サーボモーターを接続したGPIOピンのリスト。
        first_move: bool
            Trueの場合、初期化時にサーボを0度の位置に移動させる。
        conf_file: str
            キャリブレーション設定ファイルのパス。
        debug: bool
            デバッグモードを有効にするかどうかのフラグ。
        """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("pins=%s, first_move=%s, conf_file=%s",
                         pins, first_move, conf_file)

        self._pi = pi
        self.pins = pins
        self.conf_file = conf_file
        self.first_move = first_move

        self.servo_n = len(pins)

        self.servo = [
            CalibrableServo(
                self._pi, _pin, conf_file=self.conf_file, debug=False
            ) for _pin in self.pins
        ]

        if self.first_move:
            self.move_angle([0] * self.servo_n)

    def _validate_angle_list(self, angles):
        """
        角度のリストを検証する。
        有効な場合はTrue、そうでない場合はFalseを返す。

        Parameters
        ----------
        angles: list[float] or tuple[float]
            検証する角度のリストまたはタプル。

        Returns
        -------
        bool
            検証結果。
        """
        if not isinstance(angles, (list, tuple)):
            self.__log.error(
                "angles:%s must be list or tupple:%s", angles, type(angles)
            )
            return False

        if len(angles) != self.servo_n:
            self.__log.error(
                "len(%s)=%s != servo_n=%s", angles, len(angles), self.servo_n
            )
            return False

        return True

    def off(self):
        """
        すべてのサーボをオフにする。
        """
        self.__log.debug("")
        for s in self.servo:
            s.off()

    def get_pulse(self):
        """
        すべてのサーボの現在のパルス幅を取得する。

        Returns
        -------
        list[int]
            各サーボのパルス幅のリスト。
        """
        pulses = [s.get_pulse() for s in self.servo]
        self.__log.debug("pulses=%s", pulses)
        return pulses

    def move_pulse(self, pulses, forced=False):
        """
        各サーボを指定されたパルス幅に動かす。

        Parameters
        ----------
        pulses: list[int]
            各サーボに設定するパルス幅のリスト。
        forced: bool
            Trueの場合、可動範囲外のパルス幅も強制的に設定する。
        """
        for i, s in enumerate(self.servo):
            self.__log.debug(f"pin=s.pin, pulse={pulses[i]}")
            s.move_pulse(pulses[i], forced)

    def get_angle(self):
        """
        すべてのサーボの現在の角度を取得する。

        Returns
        -------
        list[float]
            各サーボの角度のリスト。
        """
        angles = [s.get_angle() for s in self.servo]
        self.__log.debug("angles=%s", angles)
        return angles

    def move_angle(self, angles):
        """
        各サーボを指定された角度に動かす。

        Parameters
        ----------
        angles: list[float]
            各サーボに設定する角度のリスト。
        """
        self.__log.debug("angles=%s", angles)

        if not self._validate_angle_list(angles):
            return

        for _i, _s in enumerate(self.servo):
            # self.__log.debug(f"pin={_s.pin}, angle={angles[_i]}")
            _s.move_angle(angles[_i])

    def move_angle_sync(
        self, target_angles,
        estimated_sec=DEF_ESTIMATED_TIME,
        step_n=DEF_STEP_N
    ):
        """
        すべてのサーボを目標角度まで同期的かつ滑らかに動かす。
        角度は、数値だけでなく、文字列、Noneでも指定できる。

        Parameters
        ----------
        target_angles: list[float]
            各サーボの目標角度のリスト。
            None: 現在の角度(つまり、動かさない)
            文字列: "center", "min", "max"
        estimated_sec: float
            動作にかかるおおよその時間（秒）。
        step_n: int
            動作を分割するステップ数。
            1以下の場合は、move_angle() を呼び出して、ダイレクトに動かす
        """
        self.__log.debug(
            "target_angles=%s, estimated_sec=%s, step_n=%s",
            target_angles,
            estimated_sec,
            step_n
        )

        if not self._validate_angle_list(target_angles):
            return

        # step_n が１以下の場合は、ダイレクトに動かす
        if step_n <= 1:
            self.move_angle(target_angles)
            return

        _step_sec = estimated_sec / step_n
        self.__log.debug("_step_sec=%.3f", _step_sec)

        _start_angles = self.get_angle()
        self.__log.debug("_start_angles=%s", _start_angles)

        # target_anglesを数値(角度)に変換
        _num_target_angles = []
        for i, _angle in enumerate(target_angles):
            _servo = self.servo[i]

            if isinstance(_angle, str):
                if _angle == _servo.POS_CENTER:
                    _num_target_angles.append(
                        _servo.ANGLE_CENTER
                    )
                elif _angle == _servo.POS_MIN:
                    _num_target_angles.append(
                        _servo.ANGLE_MIN
                    )
                elif _angle == _servo.POS_MAX:
                    _num_target_angles.append(
                        _servo.ANGLE_MAX
                    )
                else:  # 不明な文字: 動かさない
                    self.__log.warning(
                        "invalid word %a: ignored", _angle
                    )
                    _num_target_angles.append(_start_angles[i])

            elif _angle is None:  # None は、「動かさない」の意味
                _num_target_angles.append(_start_angles[i])

            else:  # num
                # clip: ANGLE_MIN <= _angle <= ANGLE_MAX
                _angle = max(min(_angle, _servo.ANGLE_MAX), _servo.ANGLE_MIN)
                _num_target_angles.append(_angle)

        self.__log.debug("_num_target_angles=%s", _num_target_angles)

        _diff_angles = [
            _num_target_angles[i] - _start_angles[i]
            for i in range(self.servo_n)
        ]
        self.__log.debug("_diff_angles=%s", _diff_angles)

        for _step_i in range(1, step_n + 1):
            next_angles = [
                _start_angles[i] + _diff_angles[i] * _step_i / step_n
                for i in range(self.servo_n)
            ]

            self.move_angle(next_angles)
            # self.__log.debug(
            #     "step %s/%s: next_angles=%s, _step_sec=%s",
            #     _step_i, step_n, next_angles, _step_sec
            # )
            time.sleep(_step_sec)
