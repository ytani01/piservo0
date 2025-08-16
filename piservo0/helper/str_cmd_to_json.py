#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_to_json.py."""
import json
from typing import Any, Dict, List, Optional, Union

from piservo0.utils.my_logger import get_logger


class StrCmdToJson:
    """String Command to JSON."""
    
    # コマンド文字列とJSONコマンド名のマッピング
    COMMAND_MAP: Dict[str, str] = {
        # main move command
        "mv": "move_all_angles_sync",
        # move paramters
        "sl": "sleep",
        "ms": "move_sec",
        "st": "step_n",
        "is": "interval",
        # for calibration
        "mp": "move_all_pulses_relative",
        "sc": "set",  # set center
        "sn": "set",  # set min
        "sx": "set",  # set max
        # cancel
        "ca": "cancel",
        "zz": "cancel",
    }

    # 'mv'コマンドの角度パラメータのエイリアスマッピング
    ANGLE_ALIAS_MAP: Dict[str, str] = {
        "x": "max",
        "n": "min",
        "c": "center",
    }

    # setコマンドのコマンドメイト`target`の対応
    SET_TARGET: Dict[str, str] = {
        "sc": "center",
        "sn": "min",
        "sx": "max",
    }

    def __init__(self, angle_factor: List =[], debug=False):
        """constractor."""
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("angle_factor=%s", angle_factor)

        self._angle_factor = angle_factor #  property

    @property
    def angle_factor(self):
        """Get angle_factor."""
        return self._angle_factor

    @angle_factor.setter
    def angle_factor(self, af: List = []):
        """Set angle_factor."""
        self._angle_factor = af

    def _create_error_data(self, strcmd: str) -> dict:
        """Create error data."""
        return {"err": strcmd}

    def _parse_angles(
            self, param_str: str
    ) -> Optional[List[Union[int, str, None]]]:
        """Parse angle parameters.
        'mv'コマンドのパラメータ文字列をパースして角度のリストを返す.

        e.g.
            "40,30,20,10"   --> [40,30,20,10]
            "-40,.,."       --> [-40,null,null]
            "mx,min,center" --> ["max","min","center"]
            "x,n,c"         --> ["max","min","center"]
            "x,.,center,20" --> ["max",null,"center",20]
        """
        parts = param_str.split(",")
        self.__log.debug("parts=%s", parts)

        angles: List[Union[int, str, None]] = []

        for part in parts:
            _p = part.strip().lower()
            if not _p:  # 空の要素は不正
                return None

            if _p == ".":  # None: 動かさない
                angles.append(None)

            elif _p in self.ANGLE_ALIAS_MAP:
                angles.append(self.ANGLE_ALIAS_MAP[_p])

            elif _p in ["max", "min", "center"]:
                angles.append(_p)

            else:  # 数値
                try:
                    angle = int(_p)
                    if not -90 <= angle <= 90:
                        return None  # 角度範囲外
                    angles.append(angle)
                except ValueError:
                    return None  # 数値に変換できない

        # self.__log.debug("angles=%s", angles)
        
        # angle_factor に応じて符号反転
        for _i in range(len(angles)):
            if _i >= len(self._angle_factor):
                break

            if isinstance(angles[_i], int):
                angles[_i] *= self._angle_factor[_i]

            elif self._angle_factor[_i] == -1:
                if angles[_i] == "min":
                    angles[_i] = "max"
                elif angles[_i] == "max":
                    angles[_i] = "min"

        self.__log.debug("angles=%s", angles)
        return angles

    def cmd_data(self, cmd_str: str) -> dict:
        """Command string to command data(dict).

        Args:
            cmd_str: "mv:40,30", "sl:0.5" のようなコマンド文字列。

        Returns: (dict)
            変換されたコマンドデータ(dict)。
            変換できない場合はエラー情報を返す。
        """
        self.__log.debug("cmd_str=%s", cmd_str)

        # 不正な文字列はエラー
        if not isinstance(cmd_str, str) or " " in cmd_str:
            return self._create_error_data(cmd_str)

        # e.g. "mv:10,20,30,40" --> cmd_parts = ["mv", "10,20,30,40"]
        cmd_parts = cmd_str.split(":", 1)

        # e.g. cmd_key = "mv"
        cmd_key = cmd_parts[0].lower()

        if cmd_key not in self.COMMAND_MAP:
            return self._create_error_data(cmd_str)

        # コマンド名の取得 e.g. "mv" --> "move_all_angles_sync"
        cmd_name = self.COMMAND_MAP[cmd_key]

        # パラメータの取得
        if len(cmd_parts) == 1:
            cmd_param_str = ""
        else:
            cmd_param_str = cmd_parts[1]
        self.__log.debug(
            "cmd_key=%s, cmd_name=%s, cmd_param_str=%s",
            cmd_key, cmd_name, cmd_param_str
        )

        # _cmd_dataの初期化
        _cmd_data: Dict[str, Any] = {"cmd": cmd_name}

        # コマンド別の処理
        try:
            if cmd_key == "mv":
                if not cmd_param_str:
                    return self._create_error_data(cmd_str)

                angles = self._parse_angles(cmd_param_str)
                if angles is None:
                    return self._create_error_data(cmd_str)

                _cmd_data["angles"] = angles

            elif cmd_key in ["sl", "ms", "is"]:
                sec = float(cmd_param_str)
                if sec < 0:
                    return self._create_error_data(cmd_str)

                _cmd_data["sec"] = sec

            elif cmd_key == "st":
                _n = int(cmd_param_str)
                if _n < 1:
                    return self._create_error_data(cmd_str)

                _cmd_data["n"] = _n

            elif cmd_key == "mp":
                pulse_diffs = [
                    int(_s) * self.angle_factor[i]
                    for i, _s in enumerate(cmd_param_str.split(","))
                ]
                self.__log.debug("pulse_diffs=%s", pulse_diffs)

                _cmd_data["pulse_diffs"] = pulse_diffs

            elif cmd_key in ("sc", "sn", "sx"):
                servo = int(cmd_param_str)
                target = self.SET_TARGET[cmd_key]

                if self.angle_factor[servo] < 0:
                    if target == "min":
                        target = "max"
                    elif target == "max":
                        target = "min"

                self.__log.debug("servo=%s, target=%s", servo, target)
                    
                _cmd_data["servo"] = servo
                _cmd_data["target"] = target

            elif cmd_key in ["ca", "zz"]:
                if cmd_param_str:  # パラメータがあってはならない
                    return self._create_error_data(cmd_str)

        except (ValueError, TypeError) as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return self._create_error_data(cmd_str)                

        self.__log.debug("_cmd_data=%s", _cmd_data)
        return _cmd_data

    def cmd_data_list(self, cmd_line: str) -> list[dict]:
        """Command line to command string list."""

        _cmd_data_list = []

        for cmd_str in cmd_line.split(" "):
            _cmd_data = self.cmd_data(cmd_str)
            self.__log.debug("cmd_data=%s", _cmd_data)

            _cmd_data_list.append(_cmd_data)

            if _cmd_data.get("err"):
                break

        return _cmd_data_list

    def jsonstr(self, cmd_line: str) -> str:
        """Dict形式をJSON文字列に変換."""
        self.__log.debug("cmd_line=%s", cmd_line)

        data = self.cmd_data_list(cmd_line)

        # もし、配列要素が一つだけなら、その要素だけを取り出す。
        # XXX T.B.D. 必要か？
        if len(data) == 1:
            data = data[0]
        
        self.__log.debug("data=\"%s\"", data)
        return json.dumps(data)
