
import json
from typing import Any, Dict, List, Optional, Union

# コマンド文字列とJSONコマンド名のマッピング
_COMMAND_MAP: Dict[str, str] = {
    "mv": "move_angle_sync",
    "sl": "sleep",
    "ms": "move_sec",
    "st": "step_n",
    "is": "interval",
    "ca": "cancel",
    "zz": "cancel",
}

# 'mv'コマンドの角度パラメータのエイリアスマッピング
_ANGLE_ALIAS_MAP: Dict[str, str] = {
    "x": "max",
    "n": "min",
    "c": "center",
}


def _create_error_json(cmdstr: str) -> str:
    """エラー用のJSON文字列を生成する"""
    return json.dumps({"err": cmdstr})


def _parse_angles(param_str: str) -> Optional[List[Union[int, str, None]]]:
    """'mv'コマンドのパラメータ文字列をパースして角度のリストを返す"""
    angles: List[Union[int, str, None]] = []
    parts = param_str.split(',')
    for part in parts:
        p = part.strip().lower()
        if not p:  # 空の要素は不正
            return None

        if p == '.':
            angles.append(None)
        elif p in _ANGLE_ALIAS_MAP:
            angles.append(_ANGLE_ALIAS_MAP[p])
        elif p in ["max", "min", "center"]:
            angles.append(p)
        else:
            try:
                angle = int(p)
                if not -90 <= angle <= 90:
                    return None  # 角度範囲外
                angles.append(angle)
            except ValueError:
                return None  # 数値に変換できない
    return angles


def str_to_json(cmdstr: str) -> str:
    """
    コマンド文字列をJSON文字列に変換する。

    Args:
        cmdstr: "mv:40,30", "sl:0.5" のようなコマンド文字列。

    Returns:
        変換されたJSON文字列。変換できない場合はエラー情報を含むJSONを返す。
    """
    if not isinstance(cmdstr, str) or ' ' in cmdstr:
        return _create_error_json(cmdstr)

    parts = cmdstr.split(':', 1)
    cmd_key = parts[0].lower()
    
    # 'ca' や 'zz' のようにパラメータがないコマンドの処理
    if len(parts) == 1:
        param_str = ""
    else:
        param_str = parts[1]


    if cmd_key not in _COMMAND_MAP:
        return _create_error_json(cmdstr)

    json_cmd = _COMMAND_MAP[cmd_key]
    result: Dict[str, Any] = {"cmd": json_cmd}

    if cmd_key == "mv":
        if not param_str:
            return _create_error_json(cmdstr)
        angles = _parse_angles(param_str)
        if angles is None:
            return _create_error_json(cmdstr)
        result["angles"] = angles
    elif cmd_key in ["sl", "ms", "is"]:
        try:
            sec = float(param_str)
            if sec < 0:
                return _create_error_json(cmdstr)
            result["sec"] = sec
        except (ValueError, TypeError):
            return _create_error_json(cmdstr)
    elif cmd_key == "st":
        try:
            n = int(param_str)
            if n < 1:
                return _create_error_json(cmdstr)
            result["n"] = n
        except (ValueError, TypeError):
            return _create_error_json(cmdstr)
    elif cmd_key in ["ca", "zz"]:
        if param_str:  # パラメータがあってはならない
            return _create_error_json(cmdstr)

    return json.dumps(result)
