# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_05_thread_multi_servo.py
(修正版)
"""
import pytest
from unittest.mock import MagicMock, patch
from piservo0.helper.thread_multi_servo import ThreadMultiServo

PINS = [17, 18]
CONF_FILE = "test_thread_servo.json"


@pytest.fixture
def mock_multi_servo_class():
    """MultiServoクラスのモックを返すフィクスチャ"""
    with patch("piservo0.helper.thread_multi_servo.MultiServo", autospec=True) as mock_ms:
        #返されるインスタンスのモックを設定
        instance = mock_ms.return_value
        instance.pins = PINS
        instance.conf_file = CONF_FILE
        instance.servo = [MagicMock(), MagicMock()]
        yield mock_ms  # クラスのモックを返す

@pytest.fixture
def mock_thread_worker_class():
    """ThreadWorkerクラスのモックを返すフィクスチャ"""
    with patch("piservo0.helper.thread_multi_servo.ThreadWorker", autospec=True) as mock_tw:
        yield mock_tw

@pytest.fixture
def thread_multi_servo(mocker_pigpio, mock_multi_servo_class, mock_thread_worker_class):
    """
    ThreadMultiServoのテスト用インスタンスと、
    それが内包するインスタンスモックを返すフィクスチャ
    """
    pi = mocker_pigpio()
    # このtmsは、内部で本物のMultiServoとThreadWorkerを作ってしまうが、
    # すぐに下の行でモックに差し替えるので問題ない。
    tms = ThreadMultiServo(pi, PINS, first_move=False, conf_file=CONF_FILE, debug=True)
    
    # 実際に作られたインスタンスをモックで上書き
    mservo_instance = mock_multi_servo_class.return_value
    worker_instance = mock_thread_worker_class.return_value
    tms._mservo = mservo_instance
    tms._worker = worker_instance
    
    return tms, mservo_instance, worker_instance


class TestThreadMultiServo:
    """ThreadMultiServoクラスのテスト"""

    def test_init(self, mocker_pigpio, mock_multi_servo_class, mock_thread_worker_class):
        """初期化のテスト"""
        pi = mocker_pigpio()
        tms = ThreadMultiServo(pi, PINS, first_move=True, conf_file=CONF_FILE, debug=True)

        # MultiServoが正しい引数で初期化されたか
        mock_multi_servo_class.assert_called_once_with(
            pi, PINS, True, CONF_FILE, debug=False
        )
        
        # ThreadWorkerが正しい引数で初期化され、startが呼ばれたか
        mservo_instance = mock_multi_servo_class.return_value
        mock_thread_worker_class.assert_called_once_with(
            mservo=mservo_instance, debug=True
        )
        mock_thread_worker_class.return_value.start.assert_called_once()

    def test_end(self, thread_multi_servo):
        """終了処理のテスト"""
        tms, mservo, worker = thread_multi_servo
        worker.is_alive.return_value = True

        tms.end()

        worker.end.assert_called_once()
        worker.join.assert_called_once()
        mservo.off.assert_called_once()

    def test_send_cmd(self, thread_multi_servo):
        """コマンド送信の基本テスト"""
        tms, _, worker = thread_multi_servo
        cmd = {"cmd": "test"}
        tms.send_cmd(cmd)
        worker.send.assert_called_with(cmd)

    def test_cancel_cmds(self, thread_multi_servo):
        """コマンドキャンセル"""
        tms, _, worker = thread_multi_servo
        tms.cancel_cmds()
        worker.clear_cmdq.assert_called_once()

    def test_move_all_angles(self, thread_multi_servo):
        """move_all_anglesが正しいコマンドを送信するかのテスト"""
        tms, _, worker = thread_multi_servo
        target_angles = [90, -90]
        
        tms.move_all_angles(target_angles)
        
        expected_cmd = {"cmd": "move_all_angles", "target_angles": target_angles}
        worker.send.assert_called_with(expected_cmd)

    def test_move_all_angles_sync(self, thread_multi_servo):
        """move_all_angles_syncが正しいコマンドを送信するかのテスト"""
        tms, _, worker = thread_multi_servo
        target_angles = [45, -45]
        move_sec = 0.5
        step_n = 20

        tms.move_all_angles_sync(target_angles, move_sec, step_n)

        expected_cmd = {
            "cmd": "move_all_angles_sync",
            "target_angles": target_angles,
            "move_sec": move_sec,
            "step_n": step_n,
        }
        worker.send.assert_called_with(expected_cmd)

    def test_move_all_angles_sync_relative(self, thread_multi_servo):
        """move_all_angles_sync_relativeが正しいコマンドを送信するかのテスト"""
        tms, _, worker = thread_multi_servo
        angle_diffs = [10, -10]
        move_sec = 0.3
        step_n = 10

        tms.move_all_angles_sync_relative(angle_diffs, move_sec, step_n)

        expected_cmd = {
            "cmd": "move_all_angles_sync_relative",
            "angle_diffs": angle_diffs,
            "move_sec": move_sec,
            "step_n": step_n,
        }
        worker.send.assert_called_with(expected_cmd)

    @pytest.mark.parametrize("sec", [0.5, 1.0])
    def test_sleep(self, thread_multi_servo, sec):
        """sleepが正しいコマンドを送信するかのテスト"""
        tms, _, worker = thread_multi_servo
        tms.sleep(sec)
        worker.send.assert_called_with({"cmd": "sleep", "sec": sec})

    def test_get_all_angles(self, thread_multi_servo):
        """get_all_anglesがMultiServoのメソッドを呼ぶかのテスト"""
        tms, mservo, _ = thread_multi_servo
        expected_angles = [10.0, 20.0]
        mservo.get_all_angles.return_value = expected_angles

        angles = tms.get_all_angles()

        mservo.get_all_angles.assert_called_once()
        assert angles == expected_angles
