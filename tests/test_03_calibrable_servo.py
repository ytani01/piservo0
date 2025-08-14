# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_03_calibrable_servo.py
(リファクタリング修正版)
"""
import pytest
from unittest.mock import MagicMock, patch
from piservo0.core.calibrable_servo import CalibrableServo
from piservo0.core.piservo import PiServo

PIN = 18
CONF_FILE = "test_servo_conf.json"


@pytest.fixture
def mock_config_manager():
    """ServoConfigManagerのモックを返すフィクスチャ"""
    with patch("piservo0.core.calibrable_servo.ServoConfigManager") as mock_scm:
        instance = mock_scm.return_value
        instance.get_config.return_value = None
        instance.conf_file = CONF_FILE
        yield instance


@pytest.fixture
def servo(mocker_pigpio, mock_config_manager):
    """CalibrableServoのテスト用インスタンスを生成するフィクスチャ"""
    pi = mocker_pigpio()
    servo_instance = CalibrableServo(pi, PIN, conf_file=CONF_FILE, debug=True)
    pi.reset_mock()
    return servo_instance


class TestCalibrableServoRefactored:
    """
    CalibrableServoクラスのリファクタリングされたテスト
    - フラットな構造
    - setup_methodでテストごとの状態を初期化
    - マジックナンバーをインスタンス変数に置き換え
    """

    def setup_method(self, method):
        """各テストメソッドの前に呼ばれるセットアップ"""
        self.PULSE_MIN = 600
        self.PULSE_CENTER = 1500
        self.PULSE_MAX = 2400
        self.ANGLE_MIN = -90.0
        self.ANGLE_CENTER = 0.0
        self.ANGLE_MAX = 90.0

    def _setup_servo_calibration(self, servo):
        """サーボのキャリブレーション値を設定するヘルパー"""
        servo._pulse_min = self.PULSE_MIN
        servo._pulse_center = self.PULSE_CENTER
        servo._pulse_max = self.PULSE_MAX

    #
    # Init Tests
    #
    def test_init_no_config(self, servo, mock_config_manager):
        """設定ファイルなしでの初期化"""
        mock_config_manager.get_config.assert_called_with(PIN)
        mock_config_manager.save_config.assert_called()
        assert servo.pulse_min == PiServo.MIN

    def test_init_with_full_config(self, mocker_pigpio, mock_config_manager):
        """完全な設定ファイルでの初期化"""
        config_data = {"pin": PIN, "min": 700, "center": 1600, "max": 2500}
        mock_config_manager.get_config.return_value = config_data
        
        pi = mocker_pigpio()
        servo = CalibrableServo(pi, PIN, conf_file=CONF_FILE, debug=True)

        assert servo.pulse_min == config_data["min"]
        assert servo.pulse_center == config_data["center"]
        assert servo.pulse_max == config_data["max"]
        mock_config_manager.save_config.assert_not_called()

    #
    # Pulse Setter Tests
    #
    def test_pulse_setters(self, servo, mock_config_manager):
        """パルス幅セッターがsave_confを呼ぶことの確認"""
        servo.pulse_min = 700
        mock_config_manager.save_config.assert_called()

    def test_pulse_setters_with_none(self, servo, mock_config_manager):
        """pulse_setter(None)が現在のパルスを使用することの確認"""
        servo.pi.get_servo_pulsewidth.return_value = 1700
        servo.pulse_center = None
        assert servo.pulse_center == 1700
        mock_config_manager.save_config.assert_called()

    def test_pulse_setter_constraints(self, servo):
        """パルス幅セッターの制約(min <= center <= max)の確認"""
        self._setup_servo_calibration(servo)
        servo.pulse_center = self.PULSE_MIN - 100
        assert servo.pulse_center == self.PULSE_MIN

    #
    # Angle Conversion Tests
    #
    @pytest.mark.parametrize("deg, expected_pulse_calc", [
        (0.0, "self.PULSE_CENTER"),
        (90.0, "self.PULSE_MAX"),
        (-90.0, "self.PULSE_MIN"),
        (45.0, "(self.PULSE_CENTER + self.PULSE_MAX) // 2"),
    ])
    def test_conversion_deg2pulse(self, servo, deg, expected_pulse_calc):
        """deg2pulseのパラメータ化テスト"""
        self._setup_servo_calibration(servo)
        expected_pulse = eval(expected_pulse_calc)
        assert servo.deg2pulse(deg) == expected_pulse

    @pytest.mark.parametrize("pulse_calc, expected_deg", [
        ("self.PULSE_CENTER", 0.0),
        ("self.PULSE_MAX", 90.0),
        ("self.PULSE_MIN", -90.0),
    ])
    def test_conversion_pulse2deg(self, servo, pulse_calc, expected_deg):
        """pulse2degのパラメータ化テスト"""
        self._setup_servo_calibration(servo)
        pulse = eval(pulse_calc)
        assert round(servo.pulse2deg(pulse), 1) == expected_deg

    def test_conversion_get_angle(self, servo):
        """get_angleのテスト"""
        self._setup_servo_calibration(servo)
        pulse = (self.PULSE_CENTER + self.PULSE_MAX) // 2
        servo.pi.get_servo_pulsewidth.return_value = pulse
        assert round(servo.get_angle(), 1) == 45.0

    #
    # Movement Tests
    #
    @pytest.mark.parametrize("angle_in, expected_pulse_calc", [
        (45, "(self.PULSE_CENTER + self.PULSE_MAX) // 2"),
        ("min", "self.PULSE_MIN"),
        ("center", "self.PULSE_CENTER"),
        ("max", "self.PULSE_MAX"),
        (100, "self.PULSE_MAX"),
        (-100, "self.PULSE_MIN"),
    ])
    def test_movement_move_angle_calibrated(self, servo, angle_in, expected_pulse_calc):
        """キャリブレーション値を考慮したmove_angleのテスト"""
        self._setup_servo_calibration(servo)
        expected_pulse = eval(expected_pulse_calc)
        servo.move_angle(angle_in)
        servo.pi.set_servo_pulsewidth.assert_called_with(PIN, expected_pulse)

    def test_movement_move_angle_invalid_str(self, servo):
        """move_angle(無効な文字列)のテスト"""
        servo.move_angle("invalid_string")
        servo.pi.set_servo_pulsewidth.assert_not_called()

    def test_movement_move_calibrated_positions(self, servo):
        """move_center/min/maxがキャリブレーション値を使うかのテスト"""
        self._setup_servo_calibration(servo)
        servo.move_center()
        servo.pi.set_servo_pulsewidth.assert_called_with(PIN, self.PULSE_CENTER)
        servo.move_min()
        servo.pi.set_servo_pulsewidth.assert_called_with(PIN, self.PULSE_MIN)
        servo.move_max()
        servo.pi.set_servo_pulsewidth.assert_called_with(PIN, self.PULSE_MAX)

    def test_movement_move_pulse_calibrated(self, servo):
        """キャリブレーション値を考慮したmove_pulseのテスト"""
        self._setup_servo_calibration(servo)
        servo.move_pulse(self.PULSE_MIN - 100)
        servo.pi.set_servo_pulsewidth.assert_called_with(PIN, self.PULSE_MIN)

    def test_movement_move_pulse_forced(self, servo):
        """forced=Trueの場合のmove_pulseテスト"""
        self._setup_servo_calibration(servo)
        pulse = self.PULSE_MIN - 100
        servo.move_pulse(pulse, forced=True)
        servo.pi.set_servo_pulsewidth.assert_called_with(PIN, pulse)