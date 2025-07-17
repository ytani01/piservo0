import pytest
import time
import pigpio
import os
import json
from piservo0 import MultiServo

SLEEP_SEC = 1.0
TEST_PINS = [18, 21]
TEST_CONF_FILE = './test_multi_servo_conf.json'

@pytest.fixture(scope="function")
def multi_servo_setup():
    """
    MultiServoのテストセットアップとクリーンアップを行うフィクスチャ。
    """
    # テスト用の設定ファイルを作成
    conf_data = [
        {"pin": TEST_PINS[0], "min": 600, "center": 1500, "max": 2400},
        {"pin": TEST_PINS[1], "min": 700, "center": 1600, "max": 2500}
    ]
    with open(TEST_CONF_FILE, 'w') as f:
        json.dump(conf_data, f)

    pi = pigpio.pi()
    if not pi.connected:
        pytest.fail("pigpio daemon not connected.")
    
    multi_servo = MultiServo(pi, TEST_PINS, conf_file=TEST_CONF_FILE, debug=True)
    
    yield pi, multi_servo
    
    # クリーンアップ
    multi_servo.move_angle([0] * len(TEST_PINS))
    time.sleep(SLEEP_SEC)
    multi_servo.off()
    pi.stop()
    if os.path.exists(TEST_CONF_FILE):
        os.remove(TEST_CONF_FILE)

def test_initialization(multi_servo_setup):
    """
    MultiServoが正しく初期化されるかをテストする。
    """
    pi, multi_servo = multi_servo_setup
    assert isinstance(multi_servo, MultiServo)
    assert len(multi_servo.servo) == len(TEST_PINS)
    assert multi_servo.servo_n == len(TEST_PINS)
    for i, pin in enumerate(TEST_PINS):
        assert multi_servo.servo[i].pin == pin

def test_get_angle(multi_servo_setup):
    """
    get_angleが各サーボの正しい角度リストを返すかテストする。
    """
    pi, multi_servo = multi_servo_setup
    
    # 初期位置(0度)のはず
    angles = multi_servo.get_angle()
    assert len(angles) == len(TEST_PINS)
    for angle in angles:
        # 浮動小数点数の比較のため、許容誤差を設ける
        assert pytest.approx(angle, abs=1.0) == 0.0

def test_move_angle(multi_servo_setup):
    """
    move_angleで各サーボが指定された角度に移動するかをテストする。
    """
    pi, multi_servo = multi_servo_setup
    target_angles = [-45, 45]
    
    multi_servo.move_angle(target_angles)
    time.sleep(SLEEP_SEC)
    
    current_angles = multi_servo.get_angle()
    assert len(current_angles) == len(target_angles)
    for i, angle in enumerate(current_angles):
        assert pytest.approx(angle, abs=1.0) == target_angles[i]

def test_move_angle_sync(multi_servo_setup):
    """
    move_angle_syncで各サーボが同期して移動し、
    最終的に目標角度に到達するかをテストする。
    """
    pi, multi_servo = multi_servo_setup
    
    # まずは初期位置(0度)にしっかり移動させておく
    multi_servo.move_angle([0, 0])
    time.sleep(SLEEP_SEC)

    target_angles = [90, -90]
    move_sec = 1.5
    
    start_time = time.time()
    multi_servo.move_angle_sync(target_angles, estimated_sec=move_sec, step_n=20)
    end_time = time.time()

    # 実行時間が指定した時間に近いことを確認
    assert pytest.approx(end_time - start_time, abs=0.5) == move_sec

    # 最終的な角度が目標と一致することを確認
    current_angles = multi_servo.get_angle()
    assert len(current_angles) == len(target_angles)
    for i, angle in enumerate(current_angles):
        assert pytest.approx(angle, abs=1.0) == target_angles[i]

def test_off(multi_servo_setup):
    """
    offメソッドで全てのサーボが停止するかをテストする。
    """
    pi, multi_servo = multi_servo_setup
    
    multi_servo.move_angle([30, -30])
    time.sleep(SLEEP_SEC)

    # offを呼ぶ
    multi_servo.off()
    
    # 全てのサーボのパルス幅が0になっていることを確認
    pulses = multi_servo.get_pulse()
    for pulse in pulses:
        assert pulse == 0

def test_move_angle_invalid_length(multi_servo_setup, mocker):
    """
    不正な長さのリストを渡した際にエラーログが出て、
    角度が変わらないことをテストする。
    """
    pi, multi_servo = multi_servo_setup
    # multi_servoインスタンスの内部ロガーのエラーメソッドをモック化
    mocker.patch.object(multi_servo._log, 'error')

    initial_angles = multi_servo.get_angle()
    invalid_angles = [10]  # 長さが違う

    # move_angle
    multi_servo.move_angle(invalid_angles)
    # エラーログが1回呼び出されたことを確認
    multi_servo._log.error.assert_called_once()
    current_angles = multi_servo.get_angle()
    # 角度が変わっていないことを確認
    assert initial_angles == current_angles

    # move_angle_sync
    multi_servo._log.error.reset_mock()
    multi_servo.move_angle_sync(invalid_angles)
    multi_servo._log.error.assert_called_once()
    current_angles = multi_servo.get_angle()
    assert initial_angles == current_angles

def test_move_angle_invalid_type(multi_servo_setup, mocker):
    """
    不正な型の引数を渡した際にエラーログが出て、
    角度が変わらないことをテストする。
    """
    pi, multi_servo = multi_servo_setup
    mocker.patch.object(multi_servo._log, 'error')

    initial_angles = multi_servo.get_angle()
    invalid_arg = "not a list"

    # move_angle
    multi_servo.move_angle(invalid_arg)
    multi_servo._log.error.assert_called_once()
    current_angles = multi_servo.get_angle()
    assert initial_angles == current_angles

    # move_angle_sync
    multi_servo._log.error.reset_mock()
    multi_servo.move_angle_sync(invalid_arg)
    multi_servo._log.error.assert_called_once()
    current_angles = multi_servo.get_angle()
    assert initial_angles == current_angles
