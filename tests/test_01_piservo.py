import pytest
import time
import pigpio
from piservo0 import PiServo

SLEEP_SEC = 0.8
TEST_PIN = 18

@pytest.fixture(scope="function")
def servo_test_setup():
    """
    テストのセットアップとクリーンアップを行うフィクスチャ。
    各テスト関数の実行前にサーボを初期化し、実行後に停止する。
    """
    pi = pigpio.pi()
    if not pi.connected:
        pytest.fail("pigpio daemon not connected.")
    
    servo = PiServo(pi, TEST_PIN, debug=True)
    
    # テスト関数に (pi, servo) を渡す
    yield pi, servo
    
    # テスト関数実行後のクリーンアップ
    servo.move_center()
    time.sleep(SLEEP_SEC)
    servo.off()
    pi.stop()

def test_new(servo_test_setup):
    """
    PiServoオブジェクトが正しく生成されるかテストする。
    """
    pi, servo = servo_test_setup
    assert isinstance(servo, PiServo)

def test_move_center(servo_test_setup):
    """
    サーボが中央位置に正しく移動するかテストする。
    """
    pi, servo = servo_test_setup
    servo.move_center()
    time.sleep(SLEEP_SEC)
    assert servo.get_pulse() == PiServo.CENTER

def test_move_min(servo_test_setup):
    """
    サーボが最小位置に正しく移動するかテストする。
    """
    pi, servo = servo_test_setup
    servo.move_min()
    time.sleep(SLEEP_SEC)
    assert servo.get_pulse() == PiServo.MIN

def test_move_max(servo_test_setup):
    """
    サーボが最大位置に正しく移動するかテストする。
    """
    pi, servo = servo_test_setup
    servo.move_max()
    time.sleep(SLEEP_SEC)
    assert servo.get_pulse() == PiServo.MAX

@pytest.mark.parametrize(('pulse', "expected"), [
    (1000, 1000),
    (2000, 2000),
    (PiServo.MIN, PiServo.MIN),
    (PiServo.MAX, PiServo.MAX),
    (PiServo.MIN - 1, PiServo.MIN),  # 範囲外(下)
    (PiServo.MAX + 1, PiServo.MAX),  # 範囲外(上)
    (PiServo.CENTER, PiServo.CENTER),
])
def test_move_pulse(servo_test_setup, pulse, expected):
    """
    任意のパルス幅でサーボが正しく移動するかテストする。
    範囲外の値が指定された場合に、自動的に丸められるかも確認する。
    """
    pi, servo = servo_test_setup
    servo.move_pulse(pulse)
    time.sleep(SLEEP_SEC)
    assert servo.get_pulse() == expected
