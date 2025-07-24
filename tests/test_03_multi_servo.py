#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for MultiServo
"""
import json
import logging
import pytest

from unittest.mock import call
from piservo0 import MultiServo, CalibrableServo


TEST_PINS = [17, 27, 22, 23]


@pytest.fixture
def multi_servo(mocker_pigpio, tmp_path):
    """
    MultiServoのテスト用フィクスチャ。
    モック化されたpigpioと一時的な設定ファイルを使用する。
    """
    conf_file = tmp_path / "test_multi_servo_conf.json"
    conf_data = [
        {"pin": TEST_PINS[0], "min": 600, "center": 1500, "max": 2400},
        {"pin": TEST_PINS[1], "min": 700, "center": 1600, "max": 2500},
    ]
    with open(conf_file, "w") as f:
        json.dump(conf_data, f)

    pi = mocker_pigpio()
    multi_servo = MultiServo(
        pi, TEST_PINS, conf_file=str(conf_file), first_move=False, debug=True
    )

    yield pi, multi_servo


def test_constructor(multi_servo):
    """
    MultiServoが正しく初期化されるか。
    """
    _, ms = multi_servo
    assert isinstance(ms, MultiServo)
    assert len(ms.servo) == len(TEST_PINS)
    assert ms.servo_n == len(TEST_PINS)
    for i, pin in enumerate(TEST_PINS):
        assert ms.servo[i].pin == pin

    # 設定ファイルが読み込まれているか
    assert ms.servo[0].pulse_min == 600
    assert ms.servo[1].pulse_center == 1600
    # 設定ファイルにないピンはデフォルト値か
    assert ms.servo[2].pulse_max == CalibrableServo.MAX


def test_off(multi_servo):
    """
    off()ですべてのサーボのパルス幅が0に設定されるか。
    """
    pi, ms = multi_servo
    ms.off()
    calls = [call(pin, 0) for pin in TEST_PINS]
    pi.set_servo_pulsewidth.assert_has_calls(calls, any_order=True)


def test_get_angle(multi_servo):
    """
    get_angleが各サーボの正しい角度リストを返すか。
    """
    pi, ms = multi_servo
    # 各サーボのget_pulseが返す値を設定
    pi.get_servo_pulsewidth.side_effect = [1500, 1600, 1500, 1500]

    angles = ms.get_angle()

    assert len(angles) == len(TEST_PINS)
    # 0番目のサーボはpin=17, center=1500なので角度0
    assert angles[0] == pytest.approx(0)
    # 1番目のサーボはpin=27, center=1600なので角度0
    assert angles[1] == pytest.approx(0)


def test_move_angle(multi_servo):
    """
    move_angleで各サーボが指定された角度に移動するか。
    """
    pi, ms = multi_servo
    target_angles = [-45, 45, 0, 90]

    ms.move_angle(target_angles)

    # 各サーボのdeg2pulseで計算された正しいパルス幅で呼ばれているか
    calls = [
        call(ms.servo[i].pin, ms.servo[i].deg2pulse(angle))
        for i, angle in enumerate(target_angles)
    ]
    pi.set_servo_pulsewidth.assert_has_calls(calls, any_order=False)


def test_move_angle_sync(multi_servo, mocker):
    """
    move_angle_syncが滑らかな動きを生成するか（中間ステップの検証）。
    """
    pi, ms = multi_servo
    mocker.patch("time.sleep")  # time.sleepを無効化

    target_angles = [90, -90, 45, -45]
    start_angles = [0, 0, 0, 0]  # 簡単のため初期角度を0とする
    # get_angleが常にstart_anglesを返すようにモック化
    mocker.patch.object(ms, "get_angle", return_value=start_angles)

    ms.move_angle_sync(target_angles, estimated_sec=1.0, step_n=10)

    # 呼び出し回数が ステップ数 * サーボ数 であることを確認
    assert pi.set_servo_pulsewidth.call_count == 10 * len(TEST_PINS)

    # 最終的な角度が目標と一致することを確認
    final_calls = [
        call(ms.servo[i].pin, ms.servo[i].deg2pulse(angle))
        for i, angle in enumerate(target_angles)
    ]
    pi.set_servo_pulsewidth.assert_has_calls(final_calls, any_order=False)


@pytest.mark.parametrize(
    "invalid_angles",
    [
        [10],  # 長さが違う
        "not a list",  # 型が違う
    ],
)
def test_move_angle_invalid_arg(caplog, multi_servo, invalid_angles, mocker):
    caplog.set_level(logging.DEBUG)

    pi, ms = multi_servo

    ms.move_angle(invalid_angles)

    assert "len(angles)=1" in caplog.text

    """
    mocker.patch.object(ms.__log, "error")

    ms.move_angle(invalid_angles)
    ms.__log.error.assert_called_once()
    pi.set_servo_pulsewidth.assert_not_called()

    ms._log.error.reset_mock()
    pi.reset_mock()

    ms.move_angle_sync(invalid_angles)
    ms._log.error.assert_called_once()
    pi.set_servo_pulsewidth.assert_not_called()
    """
