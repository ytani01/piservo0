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
        "mp": "move_pulse_diff",
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
        """get angle_factor."""
        return self._angle_factor

    @angle_factor.setter
    def angle_factor(self, af: List = []):
        """set angle_factor."""
        self._angle_factor = af

    def _create_error_json(self, strcmd: str) -> dict:
        """エラー用のJSON文字列を生成する"""
        return {"err": strcmd}

    def _parse_angles(
            self, param_str: str
    ) -> Optional[List[Union[int, str, None]]]:
        """'mv'コマンドのパラメータ文字列をパースして角度のリストを返す.

        e.g.
            "40,30,20,10"   --> [40,30,20,10]
            "-40,.,."       --> [-40,null,null]
            "mx,min,center" --> ["max","min","center"]
            "x,n,c"         --> ["max","min","center"]
            "x,.,center,20" --> ["max",null,"center",20]
        """

        _parts = param_str.split(",")
        self.__log.debug("_parts=%s", _parts)

        _angles: List[Union[int, str, None]] = []

        for _part in _parts:
            _p = _part.strip().lower()
            if not _p:  # 空の要素は不正
                return None

            if _p == ".":  # None: 動かさない
                _angles.append(None)

            elif _p in self.ANGLE_ALIAS_MAP:
                _angles.append(self.ANGLE_ALIAS_MAP[_p])

            elif _p in ["max", "min", "center"]:
                _angles.append(_p)

            else:  # 数値
                try:
                    angle = int(_p)
                    if not -90 <= angle <= 90:
                        return None  # 角度範囲外
                    _angles.append(angle)
                except ValueError:
                    return None  # 数値に変換できない

        self.__log.debug("_angles=%s", _angles)
        
        # angle_factor に応じて符号反転
        for i in range(len(_angles)):
            if i >= len(self._angle_factor):
                break

            if isinstance(_angles[i], int):
                _angles[i] *= self._angle_factor[i]
                
            elif self._angle_factor[i] == -1:
                if _angles[i] == "min":
                    _angles[i] = "max"
                elif _angles[i] == "max":
                    _angles[i] = "min"

        self.__log.debug("_angles=%s", _angles)
        return _angles

    def json(self, strcmd: str) -> dict:
        """
        コマンド文字列をJSON文字列に変換する。

        Args:
            strcmd: "mv:40,30", "sl:0.5" のようなコマンド文字列。

        Returns:
            変換されたJSON文字列。変換できない場合はエラー情報を含むJSONを返す。
        """
        self.__log.debug("strcmd=%s", strcmd)

        # 不正な文字列はエラー
        if not isinstance(strcmd, str) or " " in strcmd:
            return self._create_error_json(strcmd)

        # e.g. "mv:10,20,30,40" --> _parts = ["mv", "10,20,30,40"]
        _parts = strcmd.split(":", 1)

        # e.g. _cmd_key = "mv"
        _cmd_key = _parts[0].lower()

        # パラメータがないコマンドの処理
        if len(_parts) == 1:
            _param_str = ""
        else:
            _param_str = _parts[1]

        if _cmd_key not in self.COMMAND_MAP:
            return self._create_error_json(strcmd)

        _cmd_name = self.COMMAND_MAP[_cmd_key]

        _json: Dict[str, Any] = {"cmd": _cmd_name}

        if _cmd_key == "mv":
            if not _param_str:
                return self._create_error_json(strcmd)

            _angles = self._parse_angles(_param_str)

            if _angles is None:
                return self._create_error_json(strcmd)

            _json["angles"] = _angles

        elif _cmd_key in ["sl", "ms", "is"]:
            try:
                sec = float(_param_str)
                if sec < 0:
                    return self._create_error_json(strcmd)

                _json["sec"] = sec

            except (ValueError, TypeError):
                return self._create_error_json(strcmd)

        elif _cmd_key == "st":
            try:
                _n = int(_param_str)
                if _n < 1:
                    return self._create_error_json(strcmd)

                _json["n"] = _n

            except (ValueError, TypeError):
                return self._create_error_json(strcmd)

        elif _cmd_key == "mp":
            try:
                servo, pulse_diff = [
                    int(s) for s in _param_str.split(",", 1)
                ]
                self.__log.debug("servo=%s, pulse_diff=%s", servo, pulse_diff)

                _json["servo"] = servo
                _json["pulse_diff"] = pulse_diff

            except (ValueError, TypeError):
                return self._create_error_json(strcmd)

        elif _cmd_key in ("sc", "sn", "sx"):
            try:
                _json["servo"] = int(_param_str)
                _json["target"] = self.SET_TARGET[_cmd_key]

            except (ValueError, TypeError):
                return self._create_error_json(strcmd)                

        elif _cmd_key in ["ca", "zz"]:
            if _param_str:  # パラメータがあってはならない
                return self._create_error_json(strcmd)

        self.__log.debug("json=%s", _json)
        return _json

    def jsonstr(self, strcmd: str) -> str:
        """コマンド文字列をJSON文字列に変換."""
        self.__log.debug("strcmd=%s", strcmd)
        return json.dumps(self.json(strcmd))
