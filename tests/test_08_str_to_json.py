
import json
import pytest
from piservo0.helper.str_to_json import str_to_json

# 正常系のテストケース
# (入力文字列, 期待されるJSON文字列)
normal_test_cases = [
    # mvコマンド
    ("mv:40,30,20,10", '{"cmd": "move_angle_sync", "angles": [40, 30, 20, 10]}'),
    ("mv:-40,.,.", '{"cmd": "move_angle_sync", "angles": [-40, null, null]}'),
    ("mv:max,min,center", '{"cmd": "move_angle_sync", "angles": ["max", "min", "center"]}'),
    ("mv:x,n,c", '{"cmd": "move_angle_sync", "angles": ["max", "min", "center"]}'),
    ("mv:X,N,C", '{"cmd": "move_angle_sync", "angles": ["max", "min", "center"]}'), # 大文字
    ("mv:x,.,center,20", '{"cmd": "move_angle_sync", "angles": ["max", null, "center", 20]}'),
    ("mv:90", '{"cmd": "move_angle_sync", "angles": [90]}'),
    ("mv:-90", '{"cmd": "move_angle_sync", "angles": [-90]}'),

    # slコマンド
    ("sl:0.5", '{"cmd": "sleep", "sec": 0.5}'),
    ("sl:1", '{"cmd": "sleep", "sec": 1}'),
    ("sl:0", '{"cmd": "sleep", "sec": 0}'),

    # msコマンド
    ("ms:1.5", '{"cmd": "move_sec", "sec": 1.5}'),

    # stコマンド
    ("st:1", '{"cmd": "step_n", "n": 1}'),
    ("st:40", '{"cmd": "step_n", "n": 40}'),

    # isコマンド
    ("is:0.5", '{"cmd": "interval", "sec": 0.5}'),

    # ca, zzコマンド
    ("ca", '{"cmd": "cancel"}'),
    ("zz", '{"cmd": "cancel"}'),
    ("CA", '{"cmd": "cancel"}'), # 大文字
]

# 異常系のテストケース
# (入力文字列, 期待されるエラーJSON文字列)
error_test_cases = [
    # 不正なコマンド
    ("xx:10", '{"err": "xx:10"}'),
    # パラメータなし
    ("mv:", '{"err": "mv:"}'),
    ("sl:", '{"err": "sl:"}'),
    # 不正なパラメータ値
    ("mv:91", '{"err": "mv:91"}'),
    ("mv:-91", '{"err": "mv:-91"}'),
    ("mv:a,b,c", '{"err": "mv:a,b,c"}'),
    ("mv:10,,20", '{"err": "mv:10,,20"}'),
    ("sl:-0.1", '{"err": "sl:-0.1"}'),
    ("sl:abc", '{"err": "sl:abc"}'),
    ("ms:-1", '{"err": "ms:-1"}'),
    ("st:0", '{"err": "st:0"}'),
    ("st:-1", '{"err": "st:-1"}'),
    ("is:-1", '{"err": "is:-1"}'),
    # 不要なパラメータ
    ("ca:1", '{"err": "ca:1"}'),
    ("zz:x", '{"err": "zz:x"}'),
    # 空白を含む
    ("mv: 10", '{"err": "mv: 10"}'),
    # 空文字列
    ("", '{"err": ""}'),
    # None
    (None, '{"err": null}'),
]

@pytest.mark.parametrize("cmdstr, expected_json_str", normal_test_cases)
def test_str_to_json_normal(cmdstr, expected_json_str):
    """正常系のテスト"""
    result = str_to_json(cmdstr)
    # JSON文字列をPythonオブジェクトに変換して比較（順序の違いを無視するため）
    assert json.loads(result) == json.loads(expected_json_str)

@pytest.mark.parametrize("cmdstr, expected_json_str", error_test_cases)
def test_str_to_json_error(cmdstr, expected_json_str):
    """異常系のテスト"""
    result = str_to_json(cmdstr)
    # errの値が元のコマンド文字列（またはNone）と一致することを確認
    expected_err = json.loads(expected_json_str)["err"]
    assert json.loads(result) == {"err": expected_err}

