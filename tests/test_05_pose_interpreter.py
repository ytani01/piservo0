#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for PoseInterpreter
"""
from unittest.mock import call
import pytest
from piservo0 import MultiServo, PoseInterpreter

TEST_PINS = [17, 27, 22, 23]


@pytest.fixture
def pose_interpreter(mocker_pigpio):
    """
    PoseInterpreterのテスト用フィクスチャ。
    """
    pi = mocker_pigpio()
    # PoseInterpreterはMultiServoを必要とする
    multi_servo = MultiServo(pi, TEST_PINS, first_move=False, debug=True)
    interpreter = PoseInterpreter(
        multi_servo, angle_factor=[-1, -1, 1, 1], debug=True
    )
    yield pi, interpreter


def test_constructor(pose_interpreter):
    """
    PoseInterpreterが正しく初期化されるか。
    """
    _, interpreter = pose_interpreter
    assert isinstance(interpreter, PoseInterpreter)
    assert interpreter.angle_factor == [-1, -1, 1, 1]


@pytest.mark.parametrize(
    "cmd_str, expected_type, expected_val_key",
    [
        ("cccc", "angles", "angles"),
        ("....", "angles", "angles"),
        ("fnxb", "angles", "angles"),
        ("FNXB", "angles", "angles"),  # 大文字
        ("1.23", "sleep", "sec"),
        ("-5", "sleep", "sec"),  # マイナスもfloat
        ("invalid", "error", "err"),
        ("ccc", "error", "err"),  # 長さが違う
    ],
)
def test_parse_cmd(pose_interpreter, cmd_str, expected_type, expected_val_key):
    """
    parse_cmdが様々なコマンド文字列を正しく解析できるか。
    """
    _, interpreter = pose_interpreter
    result = interpreter.parse_cmd(cmd_str)
    assert result["cmd"] == expected_type
    assert expected_val_key in result


def test_parse_cmd_values(pose_interpreter):
    """
    parse_cmdが返す値（角度や秒数）が正しいか。
    """
    _, interpreter = pose_interpreter

    # 'f' -> angle_unit * angle_factor
    # pin17: angle_unit(40) * factor(-1) = -40
    # pin22: angle_unit(40) * factor(1) = 40
    res = interpreter.parse_cmd("cfcf")
    assert res["cmd"] == "angles"
    angles = res["angles"]
    assert angles[0] == 0
    assert angles[1] == -40
    assert angles[2] == 0
    assert angles[3] == 40

    # 大文字は2倍
    # pin27: angle_unit(40) * factor(-1) * 2 = -80
    res = interpreter.parse_cmd("cFcF")
    angles = res["angles"]
    assert angles[0] == 0
    assert angles[1] == -80
    assert angles[2] == 0
    assert angles[3] == 80

    # sleep
    res = interpreter.parse_cmd("1.23")
    assert res["cmd"] == "sleep"
    assert res["sec"] == 1.23


def test_exec_cmd_pose(pose_interpreter, mocker):
    """
    exec_cmdがポーズコマンドを正しく実行するか。
    """
    pi, interpreter = pose_interpreter
    mocker.patch("time.sleep")

    # get_angleが常に[0,0,0,0]を返すようにして、syncの計算を単純化
    mocker.patch.object(interpreter.mservo, "get_angle", return_value=[0, 0, 0, 0])

    interpreter.exec_cmd("fccc")

    # move_angle_syncが呼ばれ、最終的にset_servo_pulsewidthが呼ばれる
    assert pi.set_servo_pulsewidth.called


def test_exec_cmd_sleep(pose_interpreter, mocker):
    """
    exec_cmdがsleepコマンドを正しく実行するか。
    """
    pi, interpreter = pose_interpreter
    mock_sleep = mocker.patch("time.sleep")

    interpreter.exec_cmd("0.5")

    mock_sleep.assert_called_once_with(0.5)
    pi.set_servo_pulsewidth.assert_not_called()


def test_exec_cmd_error(pose_interpreter, mocker):
    """
    exec_cmdが無効なコマンドでエラーログを出すか。
    """
    pi, interpreter = pose_interpreter
    mocker.patch.object(interpreter._log, "error")

    interpreter.exec_cmd("invalid")

    interpreter._log.error.assert_called_once()
    pi.set_servo_pulsewidth.assert_not_called()


@pytest.mark.parametrize(
    "seq, expected",
    [
        (["a", "b", "c"], ["a", "b", "c"]),
        (["abc", "1.0", "def"], ["cba", "1.0", "fed"]),
        (["f", "0.5", "b"], ["f", "0.5", "b"]),
    ],
)
def test_flip_sequence(pose_interpreter, seq, expected):
    """
    flip_sequenceがシーケンスを正しく反転させるか。
    """
    _, interpreter = pose_interpreter
    result = interpreter.flip_sequence(seq)
    assert result == expected
