# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_03_calibrable_servo.py
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open
from piservo0.core.calibrable_servo import CalibrableServo
from piservo0.core.piservo import PiServo
from piservo0.utils.servo_config_manager import ServoConfigManager
import json

PIN = 18
CONF_FILE = "test_servo_conf.json"


@pytest.fixture
def mock_config_manager():
    """ServoConfigManagerのモックを返すフィクスチャ"""
    with patch("piservo0.core.calibrable_servo.ServoConfigManager") as mock_scm:
        instance = mock_scm.return_value
        instance.get_config.return_value = None  # デフォルトでは設定なし
        instance.conf_file = CONF_FILE
        yield instance


@pytest.fixture
def calibrable_servo(mocker_pigpio, mock_config_manager):
    """CalibrableServoのテスト用インスタンスを生成するフィクスチャ"""
    pi = mocker_pigpio()
    servo = CalibrableServo(pi, PIN, conf_file=CONF_FILE, debug=True)
    pi.reset_mock()
    return servo


class TestCalibrableServo:
    """CalibrableServoクラスのテスト"""

    def test_init_no_config(self, calibrable_servo, mock_config_manager):
        """初期化のテスト（設定ファイルなし）"""
        assert calibrable_servo.pin == PIN
        assert calibrable_servo.pulse_min == PiServo.MIN
        assert calibrable_servo.pulse_center == PiServo.CENTER
        assert calibrable_servo.pulse_max == PiServo.MAX
        # 設定がない場合、デフォルト値でsave_confが呼ばれることを確認
        mock_config_manager.save_config.assert_called()

    def test_init_with_config(self, mocker_pigpio):
        """初期化のテスト（設定ファイルあり）"""
        # Arrange
        config_data = {
            "pin": PIN,
            "min": 600,
            "center": 1550,
            "max": 2450
        }
        # ServoConfigManagerのモックを作成し、get_configが設定を返すようにする
        with patch("piservo0.core.calibrable_servo.ServoConfigManager") as mock_scm:
            instance = mock_scm.return_value
            instance.get_config.return_value = config_data
            instance.conf_file = CONF_FILE

            # Act
            pi = mocker_pigpio()
            servo = CalibrableServo(pi, PIN, conf_file=CONF_FILE, debug=True)

            # Assert
            assert servo.pulse_min == config_data["min"]
            assert servo.pulse_center == config_data["center"]
            assert servo.pulse_max == config_data["max"]
            # 既存設定があるので、saveは呼ばれない
            instance.save_config.assert_not_called()

    def test_pulse_setters(self, calibrable_servo, mock_config_manager):
        """パルス幅セッターのテスト"""
        # pulse_min
        calibrable_servo.pulse_min = 700
        assert calibrable_servo.pulse_min == 700
        mock_config_manager.save_config.assert_called()

        # pulse_max
        calibrable_servo.pulse_max = 2300
        assert calibrable_servo.pulse_max == 2300
        mock_config_manager.save_config.assert_called()

        # pulse_center
        calibrable_servo.pulse_center = 1600
        assert calibrable_servo.pulse_center == 1600
        mock_config_manager.save_config.assert_called()

    def test_pulse_setter_constraints(self, calibrable_servo):
        """パルス幅セッターの制約テスト"""
        # centerをminより小さくしようとしてもminに補正される
        calibrable_servo.pulse_center = calibrable_servo.pulse_min - 100
        assert calibrable_servo.pulse_center == calibrable_servo.pulse_min

        # centerをmaxより大きくしようとしてもmaxに補正される
        calibrable_servo.pulse_center = calibrable_servo.pulse_max + 100
        assert calibrable_servo.pulse_center == calibrable_servo.pulse_max

        # minをcenterより大きくしようとしてもcenterに補正される
        calibrable_servo.pulse_min = calibrable_servo.pulse_center + 100
        assert calibrable_servo.pulse_min == calibrable_servo.pulse_center

        # maxをcenterより小さくしようとしてもcenterに補正される
        calibrable_servo.pulse_max = calibrable_servo.pulse_center - 100
        assert calibrable_servo.pulse_max == calibrable_servo.pulse_center

    def test_deg_pulse_conversion(self, calibrable_servo):
        """角度とパルスの変換テスト"""
        calibrable_servo.pulse_min = 600
        calibrable_servo.pulse_center = 1500
        calibrable_servo.pulse_max = 2400

        # deg -> pulse
        assert calibrable_servo.deg2pulse(0) == 1500
        assert calibrable_servo.deg2pulse(90) == 2400
        assert calibrable_servo.deg2pulse(-90) == 600
        assert calibrable_servo.deg2pulse(45) == 1950
        assert calibrable_servo.deg2pulse(-45) == 1050

        # pulse -> deg
        assert round(calibrable_servo.pulse2deg(1500), 1) == 0.0
        assert round(calibrable_servo.pulse2deg(2400), 1) == 90.0
        assert round(calibrable_servo.pulse2deg(600), 1) == -90.0
        assert round(calibrable_servo.pulse2deg(1950), 1) == 45.0
        assert round(calibrable_servo.pulse2deg(1050), 1) == -45.0

    def test_move_angle(self, calibrable_servo):
        """move_angleのテスト"""
        calibrable_servo.pulse_min = 600
        calibrable_servo.pulse_center = 1500
        calibrable_servo.pulse_max = 2400

        # 数値
        calibrable_servo.move_angle(45)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 1950)

        # 文字列
        calibrable_servo.move_angle("min")
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 600)
        calibrable_servo.move_angle("center")
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 1500)
        calibrable_servo.move_angle("max")
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 2400)

        # 範囲外
        calibrable_servo.move_angle(100)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 2400) # maxにクリップ
        calibrable_servo.move_angle(-100)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 600) # minにクリップ

        # None (何もしない)
        calibrable_servo.pi.get_servo_pulsewidth.return_value = 1500 # 現在位置
        calibrable_servo.move_angle(None)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 1500) # 現在位置を維持

    def test_move_angle_relative(self, calibrable_servo):
        """move_angle_relativeのテスト"""
        calibrable_servo.pulse_min = 600
        calibrable_servo.pulse_center = 1500
        calibrable_servo.pulse_max = 2400
        
        # 現在角度を0度(1500)に設定
        calibrable_servo.pi.get_servo_pulsewidth.return_value = 1500

        calibrable_servo.move_angle_relative(20)
        # 0度 -> 20度
        expected_pulse = calibrable_servo.deg2pulse(20)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, expected_pulse)

    def test_move_pulse_calibrated(self, calibrable_servo):
        """キャリブレーション値を考慮したmove_pulseのテスト"""
        calibrable_servo.pulse_min = 700
        calibrable_servo.pulse_max = 2300

        # 範囲内
        calibrable_servo.move_pulse(1500)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 1500)

        # 範囲外（下限）
        calibrable_servo.move_pulse(600)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 700)

        # 範囲外（上限）
        calibrable_servo.move_pulse(2400)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 2300)

    def test_move_pulse_forced(self, calibrable_servo):
        """forced=Trueの場合のmove_pulseテスト"""
        calibrable_servo.pulse_min = 700
        calibrable_servo.pulse_max = 2300

        # 範囲外でも強制的に移動
        calibrable_servo.move_pulse(600, forced=True)
        calibrable_servo.pi.set_servo_pulsewidth.assert_called_with(PIN, 600)
