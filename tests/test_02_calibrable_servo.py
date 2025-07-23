#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for CalibrableServo
"""
import json
import pytest
from piservo0 import CalibrableServo

TEST_PIN = 17


@pytest.fixture
def calib_servo(mocker_pigpio, tmp_path):
    """
    CalibrableServoのテスト用フィクスチャ。
    モック化されたpigpioと一時的な設定ファイルを使用する。
    """
    # 一時ディレクトリ内に設定ファイルのパスを作成
    conf_file = tmp_path / "test_servo_conf.json"

    # モック化されたpiインスタンスを取得
    pi = mocker_pigpio()

    # テスト対象のCalibrableServoオブジェクトを作成
    servo = CalibrableServo(pi, TEST_PIN, conf_file=str(conf_file), debug=True)

    yield pi, servo, str(conf_file)


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


def test_set_and_load_calibration(mocker_pigpio, tmp_path):
    """
    キャリブレーション値を設定・保存し、新しいインスタンスで正しく読み込むか。
    """
    conf_file = tmp_path / "test_servo_conf.json"
    pi = mocker_pigpio()

    # 1. 最初のインスタンスで値を設定・保存
    servo1 = CalibrableServo(pi, TEST_PIN, conf_file=str(conf_file))
    new_min, new_center, new_max = 1000, 1600, 2200

    # get_pulse()が返す値を設定して、setterがその値を使うようにする
    pi.get_servo_pulsewidth.return_value = new_min
    servo1.pulse_min = new_min
    pi.get_servo_pulsewidth.return_value = new_center
    servo1.pulse_center = new_center
    pi.get_servo_pulsewidth.return_value = new_max
    servo1.pulse_max = new_max

    # 2. 新しいインスタンスを作成して、値が読み込まれるか確認
    servo2 = CalibrableServo(pi, TEST_PIN, conf_file=str(conf_file))
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


def test_move_angle(calib_servo):
    """
    move_angle()が正しいパルス幅でset_servo_pulsewidthを呼び出すか。
    """
    pi, servo, _ = calib_servo

    servo.move_angle(45)
    expected_pulse = servo.deg2pulse(45)
    pi.set_servo_pulsewidth.assert_called_with(TEST_PIN, expected_pulse)

    servo.move_angle(-90)
    expected_pulse = servo.deg2pulse(-90)
    pi.set_servo_pulsewidth.assert_called_with(TEST_PIN, expected_pulse)


@pytest.mark.parametrize(
    "pos_str, expected_angle",
    [
        (CalibrableServo.POS_CENTER, CalibrableServo.ANGLE_CENTER),
        (CalibrableServo.POS_MIN, CalibrableServo.ANGLE_MIN),
        (CalibrableServo.POS_MAX, CalibrableServo.ANGLE_MAX),
    ],
)
def test_move_angle_by_string(calib_servo, pos_str, expected_angle):
    """
    'center', 'min', 'max' の文字列で角度指定移動ができるか。
    """
    pi, servo, _ = calib_servo
    servo.move_angle(pos_str)
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