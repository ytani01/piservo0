# tests/test_04_config_save.py
import os
import json
import pytest
import pigpio
from piservo0 import CalibrableServo


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


pytestmark = pytest.mark.skipif(not check_pigpiod(), reason="pigpiod is not running")


@pytest.fixture
def test_config():
    """
    テスト用の設定オブジェクトを生成するフィクスチャ。
    テストの前後で一時的な設定ファイルのクリーンアップを行う。
    """
    test_pin = 17  # 実際に使用するGPIOピン
    test_conf_file = "test_servo_config_pytest.json"

    # --- Setup ---
    pi = pigpio.pi()
    if not pi.connected:
        pytest.fail("pigpio daemon not connected.")

    if os.path.exists(test_conf_file):
        os.remove(test_conf_file)

    yield {
        "pi": pi,
        "pin": test_pin,
        "conf_file": test_conf_file,
        "new_pulse_center": 2025,
    }

    # --- Teardown ---
    pi.stop()
    if os.path.exists(test_conf_file):
        os.remove(test_conf_file)


def test_config_save_and_load(test_config):
    """
    CalibrableServoの設定を保存し、正しく読み込めるかをテストする。
    """
    # --- 1. 初期オブジェクトを作成し、値を変更して保存 ---
    servo1 = CalibrableServo(
        test_config["pi"], test_config["pin"], conf_file=test_config["conf_file"]
    )

    # 初期値がデフォルト値であることを確認
    assert servo1.pulse_center == 1500

    # 値を変更
    servo1.pulse_center = test_config["new_pulse_center"]
    assert servo1.pulse_center == test_config["new_pulse_center"]

    # 設定を保存
    servo1.save_conf()

    # ファイルが実際に書き込まれたか確認
    assert os.path.exists(test_config["conf_file"])
    with open(test_config["conf_file"], "r") as f:
        data = json.load(f)
    assert data[0]["pin"] == test_config["pin"]
    assert data[0]["center"] == test_config["new_pulse_center"]

    # --- 2. 新しいオブジェクトを作成し、値が読み込まれているか検証 ---
    servo2 = CalibrableServo(
        test_config["pi"], test_config["pin"], conf_file=test_config["conf_file"]
    )

    # 保存した値が正しく読み込まれていることを検証
    assert servo2.pulse_center == test_config["new_pulse_center"]
