#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for MultiServo
"""
import json
from unittest.mock import call

import pytest

from piservo0.core.calibrable_servo import CalibrableServo
from piservo0.core.multi_servo import MultiServo

TEST_PINS = [17, 27, 22, 23]
TEST_CONF_FILENAME = "test_multi_servo_conf.json"


@pytest.fixture
def multi_servo(mocker_pigpio, tmp_path, monkeypatch):
    """
    MultiServoのテスト用フィクスチャ。
    モック化されたpigpioと、ファイル検索ロジックを考慮した
    一時的な設定ファイルを使用する。
    """
    # 一時的なカレントディレクトリを作成し、移動
    test_cwd = tmp_path / "cwd"
    test_cwd.mkdir()
    monkeypatch.chdir(test_cwd)

    # 設定ファイルを作成
    conf_file_path = test_cwd / TEST_CONF_FILENAME
    conf_data = [
        {"pin": TEST_PINS[0], "min": 600, "center": 1500, "max": 2400},
        {"pin": TEST_PINS[1], "min": 700, "center": 1600, "max": 2500},
    ]
    with open(conf_file_path, "w") as f:
        json.dump(conf_data, f)

    pi = mocker_pigpio()
    # ファイル名のみを渡して、検索ロジックをテスト
    multi_servo_instance = MultiServo(
        pi,
        TEST_PINS,
        conf_file=TEST_CONF_FILENAME,
        first_move=False,
        debug=True,
    )

    yield pi, multi_servo_instance


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

    ms.move_angle_sync(target_angles, move_sec=1.0, step_n=10)

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
def test_invalid_arg_for_move_methods(multi_servo, invalid_angles, mocker):
    """
    move_angleとmove_angle_syncが不正な引数で呼ばれた場合、
    エラーログを記録し、サーボを動かさないことをテストする。
    """
    pi, ms = multi_servo
    # MultiServoクラスのプライベートなロガーをモック化
    mock_logger_error = mocker.patch.object(ms, "_MultiServo__log")

    # 1. move_angle のテスト
    ms.move_angle(invalid_angles)
    mock_logger_error.error.assert_called_once()
    pi.set_servo_pulsewidth.assert_not_called()

    # モックをリセット
    mock_logger_error.error.reset_mock()
    pi.reset_mock()

    # 2. move_angle_sync のテスト
    ms.move_angle_sync(invalid_angles)
    mock_logger_error.error.assert_called_once()
    pi.set_servo_pulsewidth.assert_not_called()


def test_getattr_delegation(multi_servo):
    """
    __getattr__がCalibrableServoのメソッドを正しく委譲するかテストする。
    """
    pi, ms = multi_servo

    # move_centerの呼び出しをテスト
    ms.move_center()
    expected_calls = [call(s.pin, s.pulse_center) for s in ms.servo]
    pi.set_servo_pulsewidth.assert_has_calls(expected_calls, any_order=True)

    # move_minの呼び出しをテスト
    pi.reset_mock()
    ms.move_min()
    expected_calls = [call(s.pin, s.pulse_min) for s in ms.servo]
    pi.set_servo_pulsewidth.assert_has_calls(expected_calls, any_order=True)

    # move_maxの呼び出しをテスト
    pi.reset_mock()
    ms.move_max()
    expected_calls = [call(s.pin, s.pulse_max) for s in ms.servo]
    pi.set_servo_pulsewidth.assert_has_calls(expected_calls, any_order=True)


def test_getattr_with_return_value(multi_servo, mocker):
    """
    __getattr__が値を返すメソッドを正しく処理するかテストする。
    """
    _, ms = multi_servo

    # 各サーボのdeg2pulseが特定の値を返すようにモック化
    for i, s in enumerate(ms.servo):
        mocker.patch.object(s, "deg2pulse", return_value=1000 + i)

    # MultiServo経由でdeg2pulseを呼び出す
    results = ms.deg2pulse(45)

    # 結果が各モックの返り値のリストであることを確認
    assert results == [1000, 1001, 1002, 1003]


def test_getattr_attribute_error(multi_servo):
    """
    存在しないメソッドを呼び出した場合にAttributeErrorが発生するかテストする。
    """
    _, ms = multi_servo
    with pytest.raises(AttributeError):
        ms.non_existent_method()