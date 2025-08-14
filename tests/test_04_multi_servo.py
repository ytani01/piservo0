# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_04_multi_servo.py
"""
import pytest
from unittest.mock import MagicMock, patch, call
from piservo0.core.multi_servo import MultiServo
from piservo0.core.calibrable_servo import CalibrableServo

PINS = [17, 18]
CONF_FILE = "test_multi_servo_conf.json"


@pytest.fixture
def mock_calibrable_servo():
    """CalibrableServoのモックを返すフィクスチャ"""
    with patch("piservo0.core.multi_servo.CalibrableServo", autospec=True) as mock_cs:
        # autospec=Trueで、CalibrableServoのインターフェースを持つモックを作成
        # 各インスタンスが異なる振る舞いをするように、side_effectで個別のモックを返す
        servos = [MagicMock(spec=CalibrableServo) for _ in PINS]
        for i, s in enumerate(servos):
            s.pin = PINS[i]
            s.conf_file = CONF_FILE  # conf_file属性を追加
            s.get_angle.return_value = 0.0
            s.ANGLE_MAX = 90.0
            s.ANGLE_MIN = -90.0
            s.ANGLE_CENTER = 0.0
            s.POS_MAX = "max"
            s.POS_MIN = "min"
            s.POS_CENTER = "center"

        mock_cs.side_effect = servos
        yield mock_cs, servos


@pytest.fixture
def multi_servo(mocker_pigpio, mock_calibrable_servo):
    """MultiServoのテスト用インスタンスを生成するフィクスチャ"""
    pi = mocker_pigpio()
    mock_class, mock_instances = mock_calibrable_servo
    # first_move=Falseにして、初期化時のmove_angle呼び出しをテストから分離
    ms = MultiServo(pi, PINS, first_move=False, conf_file=CONF_FILE, debug=True)
    return ms, mock_instances


class TestMultiServo:
    """MultiServoクラスのテスト"""

    def test_init(self, mocker_pigpio, mock_calibrable_servo):
        """初期化のテスト"""
        pi = mocker_pigpio()
        mock_class, mock_instances = mock_calibrable_servo
        
        # first_move=Trueでテスト
        ms = MultiServo(pi, PINS, first_move=True, conf_file=CONF_FILE, debug=True)

        assert mock_class.call_count == len(PINS)
        for pin in PINS:
            mock_class.assert_any_call(
                pi, pin, conf_file=CONF_FILE, debug=False
            )
        
        # first_move=Trueなので、各サーボのmove_angle(0)が呼ばれる
        for servo_mock in mock_instances:
            servo_mock.move_angle.assert_called_with(0)

    def test_getattr_off(self, multi_servo):
        """__getattr__によるメソッド移譲のテスト (off)"""
        ms, mock_instances = multi_servo
        ms.off()
        for servo_mock in mock_instances:
            servo_mock.off.assert_called_once()

    def test_getattr_invalid(self, multi_servo):
        """存在しないメソッド呼び出しのテスト"""
        ms, _ = multi_servo
        with pytest.raises(AttributeError):
            ms.invalid_method()

    def test_set_pulse_individual(self, multi_servo):
        """個別サーボのパルス設定テスト"""
        ms, mock_instances = multi_servo
        
        ms.set_pulse_center(0, 1600)
        assert mock_instances[0].pulse_center == 1600
        
        ms.set_pulse_min(1, 600)
        assert mock_instances[1].pulse_min == 600

        ms.set_pulse_max(0, 2400)
        assert mock_instances[0].pulse_max == 2400

    def test_move_all_angles(self, multi_servo):
        """move_all_anglesのテスト"""
        ms, mock_instances = multi_servo
        target_angles = [30, -45]
        ms.move_all_angles(target_angles)
        mock_instances[0].move_angle.assert_called_with(30)
        mock_instances[1].move_angle.assert_called_with(-45)

    def test_get_all_angles(self, multi_servo):
        """get_all_anglesのテスト"""
        ms, mock_instances = multi_servo
        mock_instances[0].get_angle.return_value = 10.0
        mock_instances[1].get_angle.return_value = -20.0
        angles = ms.get_all_angles()
        assert angles == [10.0, -20.0]

    @patch("time.sleep")
    def test_move_all_angles_sync(self, mock_sleep, multi_servo):
        """move_all_angles_syncのテスト"""
        ms, mock_instances = multi_servo
        
        start_angles = [0, 0]
        target_angles = [90, -90]
        steps = 10
        move_sec = 0.5
        
        for i, servo_mock in enumerate(mock_instances):
            servo_mock.get_angle.return_value = start_angles[i]

        ms.move_all_angles_sync(target_angles, move_sec=move_sec, step_n=steps)

        # move_all_anglesが内部で呼ぶmove_angleがsteps回呼ばれる
        assert mock_instances[0].move_angle.call_count == steps
        assert mock_instances[1].move_angle.call_count == steps
        
        # 最後の呼び出しは目標角度になっているはず
        mock_instances[0].move_angle.assert_called_with(target_angles[0])
        mock_instances[1].move_angle.assert_called_with(target_angles[1])

        assert mock_sleep.call_count == steps
        mock_sleep.assert_called_with(move_sec / steps)

    @patch("time.sleep")
    def test_move_all_angles_sync_str_none(self, mock_sleep, multi_servo):
        """move_all_angles_syncのテスト（文字列とNoneを含む）"""
        ms, mock_instances = multi_servo
        start_angles = [10, 20]
        target_angles = ["max", None]
        
        for i, servo_mock in enumerate(mock_instances):
            servo_mock.get_angle.return_value = start_angles[i]

        ms.move_all_angles_sync(target_angles, step_n=10)

        mock_instances[0].move_angle.assert_called_with(90.0)
        mock_instances[1].move_angle.assert_called_with(start_angles[1])

    def test_move_all_angles_sync_direct(self, multi_servo):
        """move_all_angles_syncのテスト（step_n=1）"""
        ms, mock_instances = multi_servo
        target_angles = [30, -45]
        ms.move_all_angles_sync(target_angles, step_n=1)
        
        mock_instances[0].move_angle.assert_called_once_with(30)
        mock_instances[1].move_angle.assert_called_once_with(-45)
