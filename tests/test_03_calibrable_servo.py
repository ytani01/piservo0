#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for CalibrableServo
"""
import json
import os
from pathlib import Path
import pytest
from piservo0 import CalibrableServo

TEST_PIN = 17
TEST_CONF_FILENAME = "test_servo_conf.json"


@pytest.fixture
def calib_servo(mocker_pigpio, tmp_path, monkeypatch):
    """
    CalibrableServoのテスト用フィクスチャ。
    モック化されたpigpioと、ファイル検索ロジックを考慮した
    一時的な設定ファイルを使用する。
    """
    # 一時的なカレントディレクトリを作成し、移動
    test_cwd = tmp_path / "cwd"
    test_cwd.mkdir()
    monkeypatch.chdir(test_cwd)

    # モック化されたpiインスタンスを取得
    pi = mocker_pigpio()

    # テスト対象のCalibrableServoオブジェクトを作成
    # ServoConfigManagerのファイル検索ロジックが働くようにファイル名のみ渡す
    servo = CalibrableServo(pi, TEST_PIN, conf_file=TEST_CONF_FILENAME, debug=True)

    # 期待される設定ファイルのフルパスも返す
    yield pi, servo, str(test_cwd / TEST_CONF_FILENAME)


def test_initial_config_creation(calib_servo):
    """
    初期化時に設定ファイルが存在しない場合、
    デフォルト値で設定ファイルが自動的に作成されるかをテストする。
    """
    _, _, conf_file = calib_servo

    with open(conf_file, "r") as f:
        config = json.load(f)

    assert len(config) == 1
    pindata = config[0]
    assert pindata["pin"] == TEST_PIN
    assert pindata["min"] == CalibrableServo.MIN
    assert pindata["center"] == CalibrableServo.CENTER
    assert pindata["max"] == CalibrableServo.MAX


def test_set_and_load_calibration(mocker_pigpio, tmp_path, monkeypatch):
    """
    キャリブレーション値を設定・保存し、新しいインスタンスで正しく読み込むか。
    """
    # CalibrableServoは内部でServoConfigManagerを使うため、
    # そのファイル検索ロジックも考慮したセットアップを行う
    test_cwd = tmp_path / "cwd"
    test_cwd.mkdir()
    monkeypatch.chdir(test_cwd)
    conf_file_path = test_cwd / TEST_CONF_FILENAME

    pi = mocker_pigpio()

    # 1. 最初のインスタンスで値を設定・保存
    servo1 = CalibrableServo(pi, TEST_PIN, conf_file=str(conf_file_path))
    new_min, new_center, new_max = 1000, 1600, 2200

    # get_pulse()が返す値を設定して、setterがその値を使うようにする
    pi.get_servo_pulsewidth.return_value = new_min
    servo1.pulse_min = new_min
    pi.get_servo_pulsewidth.return_value = new_center
    servo1.pulse_center = new_center
    pi.get_servo_pulsewidth.return_value = new_max
    servo1.pulse_max = new_max

    # 2. 新しいインスタンスを作成して、値が読み込まれるか確認
    # ここでもファイル名のみを渡して、検索ロジックを動作させる
    servo2 = CalibrableServo(pi, TEST_PIN, conf_file=TEST_CONF_FILENAME)
    assert servo2.pulse_min == new_min
    assert servo2.pulse_center == new_center
    assert servo2.pulse_max == new_max


@pytest.mark.parametrize(
    "angle, expected_pulse",
    [
        (0, 1500),
        (90, 2500),
        (-90, 500),
        (45, 2000),
        (-45, 1000),
    ],
)
def test_deg_pulse_conversion(calib_servo, angle, expected_pulse):
    """
    角度とパルス幅の相互変換が正しく行われるか（デフォルト設定）。
    """
    _, servo, _ = calib_servo
    assert servo.deg2pulse(angle) == expected_pulse
    assert servo.pulse2deg(expected_pulse) == pytest.approx(angle)


@pytest.mark.parametrize(
    "angle_or_str, expected_angle", 
    [
        (45, 45),
        (-90, -90),
        (CalibrableServo.POS_CENTER, CalibrableServo.ANGLE_CENTER),
        (CalibrableServo.POS_MIN, CalibrableServo.ANGLE_MIN),
        (CalibrableServo.POS_MAX, CalibrableServo.ANGLE_MAX),
        ('', CalibrableServo.ANGLE_MAX),
        (None, CalibrableServo.ANGLE_MAX),
    ],
)
def test_move_angle(calib_servo, angle_or_str, expected_angle):
    """
    move_angle()が数値や文字列で正しく呼び出されるか。
    """

    pi, servo, _ = calib_servo
    pi.get_servo_pulsewidth.return_value = servo.deg2pulse(expected_angle)

    servo.move_angle(angle_or_str)
    expected_pulse = servo.deg2pulse(expected_angle)
    pi.set_servo_pulsewidth.assert_called_with(TEST_PIN, expected_pulse)


def test_move_pulse_with_calibration(calib_servo):
    """
    キャリブレーション値を考慮してmove_pulseが範囲内にクリップされるか。
    """
    pi, servo, _ = calib_servo

    # キャリブレーション値を設定
    servo.pulse_min = 1000
    servo.pulse_max = 2000

    # 範囲内の値
    servo.move_pulse(1500)
    pi.set_servo_pulsewidth.assert_called_with(TEST_PIN, 1500)

    # 範囲外(下) -> クリップされる
    servo.move_pulse(900)
    pi.set_servo_pulsewidth.assert_called_with(TEST_PIN, 1000)

    # 範囲外(上) -> クリップされる
    servo.move_pulse(2100)
    pi.set_servo_pulsewidth.assert_called_with(TEST_PIN, 2000)

    # forced=True の場合はクリップされない
    servo.move_pulse(800, forced=True)
    pi.set_servo_pulsewidth.assert_called_with(TEST_PIN, 800)
