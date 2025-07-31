#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for StrControl
"""

import pytest

from piservo0.core.calibrable_servo import CalibrableServo
from piservo0.core.multi_servo import MultiServo
from piservo0.helper.str_control import StrControl

# --- 定数 ---
SERVO_N = 4
ANGLE_UNIT = 30.0
MOVE_SEC = 0.2


# --- フィクスチャ ---
@pytest.fixture
def mock_multi_servo(mocker):
    """
    MultiServoのモックオブジェクトを作成するフィクスチャ。
    StrControlのテストに特化させる。
    """
    # MultiServoのインスタンスをモック化
    mock_mservo = mocker.MagicMock(spec=MultiServo)
    mock_mservo.servo_n = SERVO_N

    # MultiServo配下のCalibrableServoオブジェクトもモック化
    mock_servos = []
    for i in range(SERVO_N):
        mock_servo = mocker.MagicMock(spec=CalibrableServo)
        mock_servo.ANGLE_MIN = -90.0
        mock_servo.ANGLE_MAX = 90.0
        mock_servo.ANGLE_CENTER = 0.0
        # get_angle()が呼ばれた際のデフォルトの戻り値を設定
        mock_servo.get_angle.return_value = 0.0
        mock_servos.append(mock_servo)

    mock_mservo.servo = mock_servos
    # get_angle()が呼ばれた際のデフォルトの戻り値を設定
    mock_mservo.get_angle.return_value = [0.0] * SERVO_N

    yield mock_mservo


@pytest.fixture
def str_control(mock_multi_servo):
    """
    テスト対象のStrControlインスタンスを作成するフィクスチャ。
    """
    scon = StrControl(
        mservo=mock_multi_servo,
        angle_unit=ANGLE_UNIT,
        move_sec=MOVE_SEC,
        debug=True
    )
    yield scon, mock_multi_servo


# --- テストケース ---

def test_constructor_default(mock_multi_servo):
    """
    デフォルト値でStrControlが正しく初期化されるか。
    """
    scon = StrControl(mservo=mock_multi_servo)
    assert scon.mservo == mock_multi_servo
    assert scon.angle_unit == StrControl.DEF_ANGLE_UNIT
    assert scon.move_sec == StrControl.DEF_MODE_SEC
    assert scon.angle_factor == [1] * SERVO_N


def test_constructor_custom(mock_multi_servo):
    """
    カスタム値でStrControlが正しく初期化されるか。
    """
    custom_angle_factor = [-1, 1, -1, 1]
    scon = StrControl(
        mservo=mock_multi_servo,
        angle_unit=45.0,
        move_sec=0.5,
        angle_factor=custom_angle_factor,
    )
    assert scon.angle_unit == 45.0
    assert scon.move_sec == 0.5
    assert scon.angle_factor == custom_angle_factor


@pytest.mark.parametrize(
    "cmd_str, expected_dict",
    [
        # 基本的なポーズコマンド
        ("cccc", {"cmd": "angles", "angles": [0.0, 0.0, 0.0, 0.0]}),
        ("ffff", {"cmd": "angles", "angles": [30.0, 30.0, 30.0, 30.0]}),
        ("bbbb", {"cmd": "angles", "angles": [-30.0, -30.0, -30.0, -30.0]}),
        ("fbcb", {"cmd": "angles", "angles": [30.0, -30.0, 0.0, -30.0]}),
        # 大文字と'.'を含む応用的なコマンド
        ("F.bC", {"cmd": "angles", "angles": [60.0, 0.0, -30.0, 0.0]}),
        # 数値（スリープ）コマンド
        ("0.5", {"cmd": "sleep", "sec": 0.5}),
        ("1", {"cmd": "sleep", "sec": 1.0}),
        # エラーケース
        ("abc", {"cmd": "error", "err": "invalid length"}),
        ("fbcz", {"cmd": "error", "err": "invalid char"}),
    ],
)
def test_parse_cmd(str_control, cmd_str, expected_dict):
    """
    parse_cmdが様々なコマンド文字列を正しく解釈できるか。
    """
    scon, _ = str_control
    # 実行
    result = scon.parse_cmd(cmd_str)
    # 検証
    assert result == expected_dict


def test_parse_cmd_with_angle_factor(mock_multi_servo):
    """
    parse_cmdがangle_factorを正しく適用するか。
    """
    scon = StrControl(
        mservo=mock_multi_servo,
        angle_unit=ANGLE_UNIT,
        angle_factor=[-1, 1, -1, 1]
    )
    result = scon.parse_cmd("fbfb")
    assert result["cmd"] == "angles"
    assert result["angles"] == [-30.0, -30.0, -30.0, -30.0]


def test_exec_cmd_angles(str_control, mocker):
    """
    exec_cmdが角度コマンドを正しく実行し、MultiServoのメソッドを呼び出すか。
    """
    scon, mock_mservo = str_control
    mocker.patch.object(scon, "parse_cmd", return_value={
        "cmd": "angles",
        "angles": [30.0, -30.0, 30.0, -30.0]
    })

    scon.exec_cmd("fbcb")

    mock_mservo.move_angle_sync.assert_called_once_with(
        [30.0, -30.0, 30.0, -30.0], scon.move_sec, scon.step_n
    )


def test_exec_cmd_sleep(str_control, mocker):
    """
    exec_cmdがスリープコマンドを正しく実行するか。
    """
    scon, _ = str_control
    mock_sleep = mocker.patch("time.sleep")
    mocker.patch.object(scon, "parse_cmd", return_value={
        "cmd": "sleep",
        "sec": 0.5
    })

    scon.exec_cmd("0.5")

    mock_sleep.assert_called_once_with(0.5)


def test_flip_cmds():
    """
    flip_cmds静的メソッドがコマンドシーケンスを正しく反転させるか。
    """
    cmds = ["fbfb", "0.1", "cccc", "BfBf"]
    expected = ["bfbf", "0.1", "cccc", "fBfB"]
    assert StrControl.flip_cmds(cmds) == expected
