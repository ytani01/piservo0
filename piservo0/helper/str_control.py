#
# (c) 2025 Yoichi Tanibayashi
#
import time

from ..core.multi_servo import MultiServo
from ..helper.thread_multi_servo import ThreadMultiServo
from ..utils.my_logger import get_logger


class StrControl:
    """
    文字列ベースのコマンドを解釈し、
    複数のサーボモーター（MultiServo）を制御するクラス。

    'fbcb' のような文字列は、各サーボのポーズ（姿勢）を示す。
    コマンド（例: 'fbcb' や '0.5'）を実行することで、
    ロボットの歩行などの複雑な動作を簡単に実現できる。
    """

    DEF_ANGLE_UNIT = 35.0
    DEF_MODE_SEC = 0.2
    DEF_ANGLE_FACTOR = [-1, -1, 1, 1]

    # コマンド文字のデフォルト定義
    DEF_CMD_CHARS = {
        "center": "c",
        "min": "n",
        "max": "x",
        "forward": "f",
        "backward": "b",
        "dont_move": ".",
        "cancel_cmds": "z",  # MultiThread の場合、コマンドをキャンセル
    }

    def __init__(
        self,
        mservo: MultiServo | ThreadMultiServo,
        move_sec: float = DEF_MODE_SEC,
        step_n: int = MultiServo.DEF_STEP_N,
        angle_unit: float = DEF_ANGLE_UNIT,
        angle_factor: list[int] | None = None,
        cmd_chars: dict[str, str] | None = None,
        debug: bool = False,
    ):
        """
        StrControlのコンストラクタ。

        Args:
            mservo (MultiServo): 制御対象のMultiServoオブジェクト。
            angle_unit (float): 'forward'/'backward'の基本角度。
            move_sec (float): 1ポーズの移動にかける時間（秒）。
            angle_factor (list[int] | None):
                各サーボの角度に掛ける係数のリスト。
                サーボの回転方向を反転させるのに使う。
                Noneの場合、すべての要素が1になる。
            cmd_chars (dict[str, str] | None):
                ポーズを定義する文字をカスタムする場合に指定する。
            debug (bool): デバッグログを有効にするか。
        """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)

        self.mservo = mservo
        self.angle_unit = angle_unit
        self.move_sec = move_sec
        self.step_n = step_n

        self.servo_n = self.mservo.servo_n

        if angle_factor is None:
            # self.angle_factor = [1] * self.servo_n
            self.angle_factor = self.DEF_ANGLE_FACTOR
        else:
            if len(angle_factor) != self.servo_n:
                raise ValueError(
                    f"len(angle_factor) must be {self.servo_n}"
                )
            self.angle_factor = angle_factor

        # デフォルト引数に辞書などのミュータブルなオブジェクトを使うと、
        # 意図しない副作用が生じる可能性があるため、Noneをデフォルトとし、
        # ここでコピーを代入する。
        if cmd_chars is None:
            self.cmd_chars = self.DEF_CMD_CHARS.copy()
        else:
            self.cmd_chars = cmd_chars

        self.__log.debug("servo_n=%s", self.servo_n)
        self.__log.debug("angle_unit=%s", self.angle_unit)
        self.__log.debug("move_sec=%s", self.move_sec)
        self.__log.debug("angle_factor=%s", self.angle_factor)
        self.__log.debug("cmd_chars=%s", self.cmd_chars)

    def set_angle_unit(self, angle: float):
        """基本角度を設定する。"""
        if angle > 0:
            self.angle_unit = angle
        self.__log.debug("angle_unit=%s", self.angle_unit)

    def set_move_sec(self, sec: float):
        """ 移動時間を設定する。"""
        if sec >= 0:
            self.move_sec = sec
        self.__log.debug("move_sec=%s", self.move_sec)

    def _is_float_str(self, s: str) -> bool:
        """文字列がfloatに変換可能か判定する。"""
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _is_str_cmd(self, cmd: str) -> tuple[bool, str]:
        """文字列がポーズコマンドか判定する。"""
        if len(cmd) != self.servo_n:
            return False, f"'{cmd}': invalid length"

        valid_chars = list(self.cmd_chars.values())
        for char in cmd.lower():
            if char not in valid_chars:
                return False, f"'{char}': invalid char"

        return True, "True"

    def _clip(self, v, v_min, v_max):
        """値を最小値と最大値の範囲に収める。"""
        return max(min(v, v_max), v_min)

    def parse_cmd(self, cmd: str) -> dict:
        """
        単一のコマンド文字列を解析し、実行可能な辞書形式に変換する。

        Args:
            cmd (str): 'fbcb'のようなポーズ文字列、
            または'0.5'のような数値文字列。

        Returns:
            dict: 解析結果。
                  例: {'cmd': 'angles', 'angles': [-40, 0, -40, 0]}
                  例: {'cmd': 'sleep', 'sec': 0.5}
                  例: {'cmd': 'error', 'err': 'invalid command'}
        """
        self.__log.debug("cmd=%s", cmd)

        if self._is_float_str(cmd):
            return {"cmd": "sleep", "sec": float(cmd)}

        if self.cmd_chars['cancel_cmds'] in cmd:
            return {"cmd": "cancel"}

        _res, _res_str = self._is_str_cmd(cmd)
        if _res is False:
            return {"cmd": "error", "err": _res_str}

        angles = []
        for i, _ch in enumerate(cmd):
            factor = self.angle_factor[i]
            if _ch.isupper():
                factor *= 2  # 大文字の場合は角度を2倍
                _ch = _ch.lower()

            _angle = None
            _c_ch = self.cmd_chars
            _s = self.mservo.servo[i]  # CalibrableServo instance

            if _ch == _c_ch["center"]:
                _angle = _s.ANGLE_CENTER
            elif _ch == _c_ch["min"]:
                _angle = _s.ANGLE_MIN
            elif _ch == _c_ch["max"]:
                _angle = _s.ANGLE_MAX
            elif _ch == _c_ch["forward"]:
                _angle = self.angle_unit
            elif _ch == _c_ch["backward"]:
                _angle = -self.angle_unit
            elif _ch == _c_ch["dont_move"]:
                # XXXX _angle = _s.get_angle()
                _angle = None

            self.__log.debug("%s[%s],%s: _angle=%s", i, _s.pin, _ch, _angle)

            if _angle is not None:
                # `dont_move`以外は係数を適用
                if _ch != _c_ch["dont_move"]:
                    _angle *= factor

                # 可動範囲内にクリップ
                _angle = self._clip(_angle, _s.ANGLE_MIN, _s.ANGLE_MAX)

            angles.append(_angle)

        return {
            "cmd": "move_angle_sync",
            "target_angles": angles,
            "move_sec": None,
            "step_n": None,
        }

    def exec_cmd(self, cmd: str):
        """
        単一のコマンドを実行する。

        Args:
            cmd (str): ポーズ文字列またはスリープ時間。
        """
        parsed_cmd = self.parse_cmd(cmd)
        self.__log.debug("parsed_cmd=%s", parsed_cmd)

        cmd_type = parsed_cmd.get("cmd")

        #
        # mservoが、ThreadMultiServoの場合は、コマンドをダイレクトに送る
        #
        if isinstance(self.mservo, ThreadMultiServo):
            if cmd_type == "error":
                self.__log.debug("%s .. ignored", parsed_cmd["err"])
                return parsed_cmd

            if cmd_type == "cancel":
                self.mservo.cancel_cmds()
                return parsed_cmd

            self.mservo.send_cmd(parsed_cmd)
            return parsed_cmd


        #
        # mservoが、MultiServoの場合は、コマンドによってメソッドを呼び出す
        #

        if cmd_type == "move_angle_sync":
            angles = parsed_cmd.get("target_angles", [])
            self.mservo.move_angle_sync(angles, self.move_sec, self.step_n)
            return parsed_cmd

        if cmd_type == "sleep":
            sec = parsed_cmd.get("sec", 0)
            if sec > 0:
                time.sleep(sec)
            return parsed_cmd

        self.__log.warning("parsed_cmd=%s .. ignored", parsed_cmd)
        return parsed_cmd

    def exec_multi_cmds(self, cmds: str | list):
        """
        複数のコマンドを実行する。

        Args:
            cmds (str | list[str]): スペース区切りの文字列、または、リスト
        """
        self.__log.debug("cmds=%s", cmds)

        if isinstance(cmds, str):
            cmds = cmds.split()

        _return = []
        for _cmd in cmds:
            _res = self.exec_cmd(_cmd)
            self.__log.debug("_res=%s", _res)

            _return.append(_res)

        self.__log.debug("_return=%s", _return)
        return _return

    @staticmethod
    def flip_cmds(cmds: list[str]) -> list[str]:
        """
        コマンド文字列を左右反転させたシーケンスを返す。
        数値（float: スリープ秒数）はそのまま。

        Args:
            cmds (list[str]): コマンドシーケンス。

        Returns:
            list[str]: 反転されたコマンドシーケンス。
                       例: ['fcfb'] -> ['bfcf']
        """
        new_cmds = []
        for cmd in cmds:
            try:
                float(cmd)
                new_cmds.append(cmd)
            except ValueError:
                new_cmds.append(cmd[::-1])
        return new_cmds
