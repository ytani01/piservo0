# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_01_piservo.py
"""
from unittest.mock import MagicMock
import pytest
from piservo0.core.piservo import PiServo


PIN = 17


@pytest.fixture
def pi_servo(mocker_pigpio):
    """PiServoのテスト用インスタンスを生成するフィクスチャ"""
    pi = mocker_pigpio()
    servo = PiServo(pi, PIN, debug=True)
    # 各テストの前にモックの状態をリセット
    pi.reset_mock()
    return servo


class TestPiServo:
    """PiServoクラスのテスト"""

    def test_init(self, pi_servo, mocker_pigpio):
        """初期化のテスト"""
        pi = mocker_pigpio()
        assert pi_servo.pi == pi
        assert pi_servo.pin == PIN

    def test_get_pulse(self, pi_servo):
        """get_pulseのテスト"""
        pi_servo.pi.get_servo_pulsewidth.return_value = 1500
        pulse = pi_servo.get_pulse()
        pi_servo.pi.get_servo_pulsewidth.assert_called_with(PIN)
        assert pulse == 1500

    def test_move_pulse_normal(self, pi_servo):
        """move_pulseの正常系テスト"""
        pulse = 1600
        pi_servo.move_pulse(pulse)
        pi_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, pulse)

    def test_move_pulse_min_limit(self, pi_servo):
        """move_pulseの下限クリップテスト"""
        pulse = PiServo.MIN - 100
        pi_servo.move_pulse(pulse)
        pi_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, PiServo.MIN)

    def test_move_pulse_max_limit(self, pi_servo):
        """move_pulseの上限クリップテスト"""
        pulse = PiServo.MAX + 100
        pi_servo.move_pulse(pulse)
        pi_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, PiServo.MAX)

    def test_move_pulse_relative(self, pi_servo):
        """move_pulse_relativeのテスト"""
        # Arrange
        current_pulse = 1500
        pulse_diff = 100
        pi_servo.pi.get_servo_pulsewidth.return_value = current_pulse

        # Act
        pi_servo.move_pulse_relative(pulse_diff)

        # Assert
        pi_servo.pi.get_servo_pulsewidth.assert_called_with(PIN)
        pi_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, current_pulse + pulse_diff)

    def test_move_pulse_relative_off(self, pi_servo):
        """move_pulse_relativeのテスト（現在OFFの場合）"""
        # Arrange
        pi_servo.pi.get_servo_pulsewidth.return_value = 0  # OFF
        pulse_diff = 100

        # Act
        pi_servo.move_pulse_relative(pulse_diff)

        # Assert
        pi_servo.pi.get_servo_pulsewidth.assert_called_with(PIN)
        pi_servo.pi.set_servo_pulsewidth.assert_not_called()

    def test_move_min(self, pi_servo):
        """move_minのテスト"""
        pi_servo.move_min()
        pi_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, PiServo.MIN)

    def test_move_max(self, pi_servo):
        """move_maxのテスト"""
        pi_servo.move_max()
        pi_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, PiServo.MAX)

    def test_move_center(self, pi_servo):
        """move_centerのテスト"""
        pi_servo.move_center()
        pi_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, PiServo.CENTER)

    def test_off(self, pi_servo):
        """offのテスト"""
        pi_servo.off()
        pi_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, PiServo.OFF)
