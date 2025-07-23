# tests/test_05_servo_tool.py
import os
import json
import pytest
import time
import pigpio
from samples.servo_tool import CalibApp

# --- テスト設定 ---
TEST_PINS = [17, 27, 22, 23]  # テストに使用するGPIOピン
TEST_CONF_FILE = "test_servo_tool_conf.json"
SLEEP_SEC = 1.0  # サーボが動くのを待つ時間


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


@pytest.fixture
def calib_app_setup():
    """
    CalibAppのテストセットアップとクリーンアップを行うフィクスチャ。
    実際のハードウェア(pigpio)を使用してテスト環境を構築する。
    """
    # --- セットアップ ---
    if os.path.exists(TEST_CONF_FILE):
        os.remove(TEST_CONF_FILE)

    # CalibAppは内部でpigpio.pi()を呼び出すため、ここでは何もしない
    app = CalibApp(pins=TEST_PINS, conf_file=TEST_CONF_FILE, debug=True)

    # テスト関数にappインス���ンスを渡す
    yield app

    # --- クリーンアップ ---
    app.end()  # pi.stop()やservo.off()を含む
    if os.path.exists(TEST_CONF_FILE):
        os.remove(TEST_CONF_FILE)


def test_select_servo(calib_app_setup):
    """
    CalibAppのselect_servoメソッドが正しく動作するかをテストする。
    """
    app = calib_app_setup

    # 1番目のサーボを選択
    app.select_servo(1)
    assert app.selected_servo == 0  # インデックスは0

    # 2番目のサーボを選択
    app.select_servo(2)
    assert app.selected_servo == 1

    # 範囲外の数字（例: 9）で「すべて選択」になるか
    app.select_servo(9)
    assert app.selected_servo == CalibApp.SELECTED_SERVO_ALL

    # 0で「すべて選択」になるか
    app.select_servo(0)
    assert app.selected_servo == CalibApp.SELECTED_SERVO_ALL


def test_move_angle_single_servo(calib_app_setup):
    """
    単一のサーボを選択し、move_angleで正しく移動するかをテストする。
    """
    app = calib_app_setup

    # 1番目のサーボを選択
    app.select_servo(1)

    target_angle = 45.0
    app.move_angle(target_angle)
    time.sleep(SLEEP_SEC)

    # 選択したサーボの角度のみが変化していることを確認
    current_angles = app.mservo.get_angle()
    assert pytest.approx(current_angles[0], abs=1.0) == target_angle
    assert pytest.approx(current_angles[1], abs=1.0) == 0.0


def test_move_angle_all_servos(calib_app_setup):
    """
    すべてのサーボを選択し、move_angleで正しく移動するかをテストする。
    """
    app = calib_app_setup

    # すべてのサーボを選択
    app.select_servo(0)

    target_angle = -30.0
    app.move_angle(target_angle)
    time.sleep(SLEEP_SEC)

    current_angles = app.mservo.get_angle()
    assert pytest.approx(current_angles[0], abs=1.0) == target_angle
    assert pytest.approx(current_angles[1], abs=1.0) == target_angle


def test_set_calibration_and_save(calib_app_setup):
    """
    キャリブレーション値を設定し、正しくファイルに保存されるかをテストする。
    min, center, maxのそれぞれが保存されることを確認する。
    """
    app = calib_app_setup

    # 1番目のサーボを選択
    app.select_servo(1)

    # --- centerの保存テスト ---
    center_pulse = 1500
    app.mservo.servo[0].move_pulse(center_pulse, forced=True)
    time.sleep(SLEEP_SEC)
    app.set_calibration("center")

    # --- minの保存テスト ---
    min_pulse = 1000
    app.mservo.servo[0].move_pulse(min_pulse, forced=True)
    time.sleep(SLEEP_SEC)
    app.set_calibration("min")

    # --- maxの保存テスト ---
    max_pulse = 2000
    app.mservo.servo[0].move_pulse(max_pulse, forced=True)
    time.sleep(SLEEP_SEC)
    app.set_calibration("max")

    # ファイルが保存されたか確認
    assert os.path.exists(TEST_CONF_FILE)

    # ファイルの内容を読み込んで検証
    with open(TEST_CONF_FILE, "r") as f:
        config_data = json.load(f)

    # TEST_PINS[0] (17) の設定を確認
    servo_config = next(
        (item for item in config_data if item["pin"] == TEST_PINS[0]), None
    )
    assert servo_config is not None
    assert servo_config["center"] == center_pulse
    assert servo_config["min"] == min_pulse
    assert servo_config["max"] == max_pulse

    # アプリケーションを再起動して設定が読み込まれることを確認する
    # CalibAppの設計上、pigpio.pi()のインスタンスを外部から
    # 注入できないため、ここで新しいCalibAppインスタンスを作成すると
    # pigpioの二重初期化でエラーになる可能性がある。
    # そのため、ここではファイルの内容が正しいことの確認に留める。
    # 実際の動作確認は手動テストまたは別の方法で行う必要がある。
    pass
