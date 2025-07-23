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

    DEF_ESTIMATED_TIME = 0.5  # sec
    DEF_STEP_N = 50
    
    def __init__(
        self,
        pi,
        pins,
        first_move=True,
        conf_file=CalibrableServo.DEF_CONF_FILE,
        debug=False,
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
        self.__log.debug("pins=%s, conf_file=%s", pins, conf_file)

        self.pi = pi
        self.pins = pins
        self.servo_n = len(pins)
        self.conf_file = conf_file
        self.first_move = first_move

        self.servo = [
            CalibrableServo(pi, pin, conf_file=self.conf_file, debug=False)
            for pin in pins
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
                f"角度はリストまたはタプル: {type(angles)}"
            )
            return False

        if len(angles) != self.servo_n:
            self.__log.error(
                f"len(angles)={len(angles)} != servo_n={self.servo_n}"
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
        self.__log.debug(f"pulses={pulses}")
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
        self.__log.debug(f"angles={angles}")
        return angles

    def move_angle(self, angles):
        """
        各サーボを指定された角度に動かす。

        Parameters
        ----------
        angles: list[float]
            各サーボに設定する角度のリスト。
        """
        self.__log.debug(f"angles={angles}")

        if not self._validate_angle_list(angles):
            return

        for i, s in enumerate(self.servo):
            self.__log.debug(f"pin={s.pin}, angle={angles[i]}")
            s.move_angle(angles[i])

    def move_angle_sync(
        self,
        target_angles,
        estimated_sec=DEF_ESTIMATED_TIME,
        step_n=DEF_STEP_N
    ):
        """
        すべてのサーボを目標角度まで同期的かつ滑らかに動かす。

        Parameters
        ----------
        target_angles: list[float]
            各サーボの目標角度のリスト。
        estimated_sec: float
            動作にかかるおおよその時間（秒）。
        step_n: int
            動作を分割するステップ数。
        """
        self.__log.debug(
            "target_angles=%s, estimated_sec=%s, step_n=%s",
            target_angles,
            estimated_sec,
            step_n,
        )

        if not self._validate_angle_list(target_angles):
            return

        if step_n < 1:
            self.move_angle(target_angles)
            return

        step_sec = estimated_sec / step_n
        self.__log.debug(f"step_sec={step_sec}")

        start_angles = self.get_angle()
        self.__log.debug(f"start_angles={start_angles}")

        # 文字列を数値に変換
        processed_target_angles = []
        for i, angle in enumerate(target_angles):
            if isinstance(angle, str):
                # 各サーボインスタンスの定数を使って変換
                servo_instance = self.servo[i]
                if angle == servo_instance.POS_CENTER:
                    processed_target_angles.append(
                        servo_instance.ANGLE_CENTER
                    )
                elif angle == servo_instance.POS_MIN:
                    processed_target_angles.append(
                        servo_instance.ANGLE_MIN
                    )
                elif angle == servo_instance.POS_MAX:
                    processed_target_angles.append(
                        servo_instance.ANGLE_MAX
                    )
                else:
                    # 不明な文字列の場合は現在の角度を維持
                    # （エラーログはmove_angleで出力）
                    self.__log.warning(
                        f'不明な角度文字列 "{angle}" を無視します。'
                    )
                    processed_target_angles.append(start_angles[i])
            else:
                processed_target_angles.append(angle)

        diff_angles = [
            processed_target_angles[i] - start_angles[i]
            for i in range(self.servo_n)
        ]
        self.__log.debug(f"diff_angles={diff_angles}")

        for step_i in range(1, step_n + 1):
            next_angles = [
                start_angles[i] + diff_angles[i] * step_i / step_n
                for i in range(self.servo_n)
            ]
            self.move_angle(next_angles)
            self.__log.debug(
                f"step {step_i}/{step_n}: "
                + f"next_angles={next_angles}, "
                + f"step_sec={step_sec}"
            )
            time.sleep(step_sec)
