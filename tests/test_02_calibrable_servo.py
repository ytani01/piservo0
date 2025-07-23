import json
import time
import os
import pigpio
import pytest

from piservo0 import CalibrableServo

SLEEP_SEC = 0.8
TEST_PIN = 17
TEST_CONF_FILE = "./test_servo_conf.json"


def check_pigpiod():
    """Check if pigpiod is running"""
    try:
        pi = pigpio.pi()
        if not pi.connected:
            return False
        pi.stop()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not check_pigpiod(), reason="pigpiod is not running"
)


@pytest.fixture(scope="function")
def calib_servo_setup():
    """
    CalibrableServoのテストセットアップとクリーンアップを行うフィクスチャ。
    """
    # テスト用の設定ファイルが残っていたら削除
    if os.path.exists(TEST_CONF_FILE):
        os.remove(TEST_CONF_FILE)

    pi = pigpio.pi()
    if not pi.connected:
        pytest.fail("pigpio daemon not connected.")

    servo = CalibrableServo(
        pi, TEST_PIN, conf_file=TEST_CONF_FILE, debug=True
    )

    yield pi, servo

    # クリーンアップ
    servo.move_center()
    time.sleep(SLEEP_SEC)
    servo.off()
    pi.stop()
    if os.path.exists(TEST_CONF_FILE):
        os.remove(TEST_CONF_FILE)


def test_initial_config_creation(calib_servo_setup):
    """
    初期化時に設定ファイルが存在しない場合、
    デフォルト値で設定ファイルが自動的に作成されるかをテストする。
    """
    assert os.path.exists(TEST_CONF_FILE)
    with open(TEST_CONF_FILE, "r") as f:
        config = json.load(f)

    assert len(config) == 1
    assert config[0]["pin"] == TEST_PIN
    assert config[0]["min"] == CalibrableServo.MIN
    assert config[0]["center"] == CalibrableServo.CENTER
    assert config[0]["max"] == CalibrableServo.MAX


def test_set_and_load_calibration():
    """
    キャリブレーション値を設定し、それがファ��ルに保存され、
    新しいインスタンスで正しく読み込まれるかをテストする。
    このテストはライフサイクルが複雑なため、フィクスチャを使用しない。
    """
    # --- セットアップ1 ---
    if os.path.exists(TEST_CONF_FILE):
        os.remove(TEST_CONF_FILE)

    pi1 = pigpio.pi()
    if not pi1.connected:
        pytest.fail("pigpio daemon not connected (first connection).")
    servo1 = CalibrableServo(
        pi1, TEST_PIN, conf_file=TEST_CONF_FILE, debug=True
    )

    # --- アクション1: 値を設定して保存 ---
    new_min = 1000
    new_center = 1500
    new_max = 2000

    servo1.move_pulse(new_min, forced=True)
    time.sleep(SLEEP_SEC)
    servo1.pulse_min = new_min

    servo1.move_pulse(new_center, forced=True)
    time.sleep(SLEEP_SEC)
    servo1.pulse_center = new_center

    servo1.move_pulse(new_max, forced=True)
    time.sleep(SLEEP_SEC)
    servo1.pulse_max = new_max

    assert servo1.pulse_min == new_min
    assert servo1.pulse_center == new_center
    assert servo1.pulse_max == new_max

    # --- クリーンアップ1 ---
    servo1.move_center()
    time.sleep(SLEEP_SEC)
    servo1.off()
    pi1.stop()

    # --- セットアップ2 & アクション2: 再度読み込んで確認 ---
    pi2 = pigpio.pi()
    if not pi2.connected:
        pytest.fail("pigpio daemon not connected (second connection).")
    servo2 = CalibrableServo(pi2, TEST_PIN, conf_file=TEST_CONF_FILE)

    assert servo2.pulse_min == new_min
    assert servo2.pulse_center == new_center
    assert servo2.pulse_max == new_max

    # --- 最終クリーンアップ ---
    servo2.move_center()
    time.sleep(SLEEP_SEC)
    servo2.off()
    pi2.stop()
    if os.path.exists(TEST_CONF_FILE):
        os.remove(TEST_CONF_FILE)


def test_move_angle(calib_servo_setup):
    """
    角度を指定してサーボが移動するかをテストする。
    """
    pi, servo = calib_servo_setup

    servo.move_angle(0)
    time.sleep(SLEEP_SEC)
    assert servo.get_pulse() == servo.deg2pulse(0)

    servo.move_angle(-90)
    time.sleep(SLEEP_SEC)
    assert servo.get_pulse() == servo.deg2pulse(-90)

    servo.move_angle(90)
    time.sleep(SLEEP_SEC)
    assert servo.get_pulse() == servo.deg2pulse(90)


@pytest.mark.parametrize(
    "pos_str, expected_angle",
    [
        (CalibrableServo.POS_CENTER, CalibrableServo.ANGLE_CENTER),
        (CalibrableServo.POS_MIN, CalibrableServo.ANGLE_MIN),
        (CalibrableServo.POS_MAX, CalibrableServo.ANGLE_MAX),
    ],
)
def test_move_angle_by_string(calib_servo_setup, pos_str, expected_angle):
    """
    'center', 'min', 'max' の文字列で角度指定移動ができるかをテストする。
    """
    pi, servo = calib_servo_setup

    servo.move_angle(pos_str)
    time.sleep(SLEEP_SEC)

    # 角度をパルス幅に変換して比較
    expected_pulse = servo.deg2pulse(expected_angle)
    assert servo.get_pulse() == expected_pulse
