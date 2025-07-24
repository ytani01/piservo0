#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for ThreadWorker
"""
import json
import time
import pytest
import threading
from unittest.mock import MagicMock
from piservo0 import ThreadWorker, MultiServo

# --- ヘルパー関数 ---

def wait_for_call(mock_obj, timeout=1.0):
    """
    モックオブジェクトが呼び出されるのを待機する。
    """
    start_time = time.time()
    while not mock_obj.called:
        if time.time() - start_time > timeout:
            raise TimeoutError("Mock was not called within the timeout period.")
        time.sleep(0.01)

# --- フィクスチャ ---

@pytest.fixture
def mock_multi_servo(mocker):
    """
    MultiServoのモックオブジェクトを作成するフィクスチャ。
    """
    mock_mservo = mocker.MagicMock(spec=MultiServo)
    mock_mservo.DEF_ESTIMATED_TIME = 0.2
    mock_mservo.DEF_STEP_N = 40
    yield mock_mservo


@pytest.fixture
def worker(mock_multi_servo):
    """
    ThreadWorkerのテスト用フィクスチャ。
    テストの開始時にスレッドを開始し、終了時に安全に停止させる。
    """
    worker_instance = ThreadWorker(mservo=mock_multi_servo, debug=True)
    worker_instance.start()
    yield worker_instance, mock_multi_servo
    worker_instance.end()


# --- テストケース ---

def test_initialization(mock_multi_servo):
    """
    ThreadWorkerが正しく初期化されるかテストする。
    """
    worker = ThreadWorker(mservo=mock_multi_servo, move_sec=0.5, step_n=50)
    assert worker.mservo == mock_multi_servo
    assert worker.move_sec == 0.5
    assert worker.step_n == 50
    assert not worker.is_alive()

def test_start_and_end(worker):
    """
    スレッドが正常に開始・終了できるかテストする。
    """
    worker_instance, _ = worker
    assert worker_instance.is_alive()

def test_send_angle_command_as_dict(worker):
    """
    辞書形式の 'angles' コマンドを送信し、正しく処理されるかテストする。
    """
    worker_instance, mock_mservo = worker
    cmd = {"cmd": "angles", "angles": [30, 0, -30, 0]}
    
    worker_instance.send(cmd)
    wait_for_call(mock_mservo.move_angle_sync)
    
    mock_mservo.move_angle_sync.assert_called_once_with(
        [30, 0, -30, 0], worker_instance.move_sec, worker_instance.step_n
    )

def test_send_angle_command_as_json(worker):
    """
    JSON文字列形式の 'angles' コマンドを送信し、正しく処理されるかテストする。
    """
    worker_instance, mock_mservo = worker
    cmd_dict = {"cmd": "angles", "angles": [45, 45, 45, 45]}
    cmd_json = json.dumps(cmd_dict)
    
    worker_instance.send(cmd_json)
    wait_for_call(mock_mservo.move_angle_sync)
    
    mock_mservo.move_angle_sync.assert_called_once_with(
        [45, 45, 45, 45], worker_instance.move_sec, worker_instance.step_n
    )

@pytest.mark.parametrize(
    "cmd_dict, expected_attr, expected_value",
    [
        ({"cmd": "move_sec", "sec": 1.5}, "move_sec", 1.5),
        ({"cmd": "step_n", "n": 50}, "step_n", 50),
        ({"cmd": "interval", "sec": 0.5}, "interval_sec", 0.5),
    ]
)
def test_send_parameter_commands(worker, cmd_dict, expected_attr, expected_value):
    """
    パラメータ変更コマンドが正しく処理されるかテストする。
    """
    worker_instance, _ = worker
    
    # パラメータが変更されるまで待機する
    timeout = 1.0
    start_time = time.time()
    
    worker_instance.send(cmd_dict)
    
    while getattr(worker_instance, expected_attr) != expected_value:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Attribute '{expected_attr}' was not updated.")
        time.sleep(0.01)

    assert getattr(worker_instance, expected_attr) == expected_value

def test_send_sleep_command(worker, mocker):
    """
    'sleep' コマンドが正しく処理されるかテストする。
    threading.Eventを使用して、スレッド間の同期を確実に行う。
    """
    worker_instance, _ = worker
    
    # time.sleepをモック化する代わりに、Eventを使って処理の完了を待つ
    sleep_called_event = threading.Event()
    original_sleep = time.sleep

    def mock_sleep(sec):
        # 呼び出された引数を記録し、イベントをセット
        mock_sleep.called_sec = sec
        sleep_called_event.set()
        # 実際のsleepは呼ばない
    
    mocker.patch("piservo0.thread_worker.time.sleep", side_effect=mock_sleep)

    cmd = {"cmd": "sleep", "sec": 1.23}
    worker_instance.send(cmd)
    
    # イベントがセットされるのを待つ（タイムアウト付き）
    event_was_set = sleep_called_event.wait(timeout=1.0)
    
    assert event_was_set, "sleep command was not processed in time."
    assert mock_sleep.called_sec == 1.23

def test_invalid_command(worker, mocker):
    """
    無効なコマンドを送信した場合にエラーログが出力されるかテストする。
    """
    worker_instance, mock_mservo = worker
    mock_logger = mocker.patch.object(worker_instance, "_ThreadWorker__log")
    
    cmd = {"cmd": "invalid_command"}
    worker_instance.send(cmd)
    
    wait_for_call(mock_logger.error)
    
    mock_logger.error.assert_called_once()
    mock_mservo.move_angle_sync.assert_not_called()
