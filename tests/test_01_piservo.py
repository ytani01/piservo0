#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for PiServo
"""
import pytest

from piservo0 import PiServo

TEST_PIN = 17


@pytest.fixture
def pi_servo(mocker_pigpio):
    """
    PiServoのテスト用フィクスチャ。
    モック化されたpigpio.piインスタンスを使ってPiServoを初期化する。
    """
    # mocker_pigpioフィクスチャはモック化されたpi()コンストラクタそのもの
    # これを呼び出して、モック化されたpiインスタンスを取得
    pi = mocker_pigpio()

    # テスト対象のPiServoオブジェクトを作成
    servo = PiServo(pi, TEST_PIN, debug=True)

    # テスト関数に (pi_mock, servo_instance) を渡す
    yield pi, servo


def test_constructor(pi_servo):
    """
    PiServoオブジェクトが正しく生成されるかテストする。
    """
    _, servo = pi_servo
    assert isinstance(servo, PiServo)
    assert servo.pin == TEST_PIN


def test_get_pulse(pi_servo):
    """
    get_pulse()が正しくpigpioのメソッドを呼び出すかテストする。
    """
    pi, servo = pi_servo
    pi.get_servo_pulsewidth.return_value = 1234

    pulse = servo.get_pulse()

    pi.get_servo_pulsewidth.assert_called_once_with(TEST_PIN)
    assert pulse == 1234


@pytest.mark.parametrize(
    ("method_name", "expected_pulse"),
    [
        ("move_center", PiServo.CENTER),
        ("move_min", PiServo.MIN),
        ("move_max", PiServo.MAX),
        ("off", PiServo.OFF),
    ],
)
def test_simple_move_methods(pi_servo, method_name, expected_pulse):
    """
    move_center(), move_min(), move_max(), off() が、
    対応する定数のパルス幅で set_servo_pulsewidth を呼び出すかテストする。
    """
    pi, servo = pi_servo
    
    # 文字列から呼び出すメソッドを取得
    method_to_call = getattr(servo, method_name)
    method_to_call()
    
    pi.set_servo_pulsewidth.assert_called_once_with(TEST_PIN, expected_pulse)


@pytest.mark.parametrize(
    ("pulse", "expected"),
    [
        (1000, 1000),
        (PiServo.MIN, PiServo.MIN),
        (PiServo.MAX, PiServo.MAX),
        (PiServo.CENTER, PiServo.CENTER),
        (PiServo.MIN - 1, PiServo.MIN),  # 範囲外(下)はMINに丸められる
        (PiServo.MAX + 1, PiServo.MAX),  # 範囲外(上)はMAXに丸められる
    ],
)
def test_move_pulse(pi_servo, pulse, expected):
    """
    move_pulse()が指定されたパルス幅で正しく呼び出されるか。
    範囲外の値が自動的にクリップされるかも確認する。
    """
    pi, servo = pi_servo
    servo.move_pulse(pulse)
    pi.set_servo_pulsewidth.assert_called_once_with(TEST_PIN, expected)
