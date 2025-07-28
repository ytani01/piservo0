#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for ThreadWorker
"""
import json
import time
import pytest
from unittest.mock import MagicMock, ANY, call
from piservo0.helper.thread_worker import ThreadWorker
from piservo0.core.multi_servo import MultiServo


# --- フィクスチャ ---

@pytest.fixture
def mock_multi_servo(mocker):
    """MultiServoのモックオブジェクトを作成するフィクスチャ。"""
    mock_mservo = mocker.MagicMock(spec=MultiServo)
    mock_mservo.DEF_MOVE_SEC = 0.2
    mock_mservo.DEF_STEP_N = 40
    return mock_mservo


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


# --- ヘルパー関数 ---

def wait_for_call(mock_obj, timeout=1.0):
    """モックオブジェクトが呼び出されるのを待機する。"""
    start_time = time.time()
    while not mock_obj.called:
        if time.time() - start_time > timeout:
            raise TimeoutError("Mock was not called within the timeout period.")
        time.sleep(0.01)


# --- テストケース ---

def test_initialization(mock_multi_servo):
    """
    ThreadWorkerが正しく初期化されるかテストする。
    """
    # デフォルト値を使用する場合
    worker_def = ThreadWorker(mservo=mock_multi_servo)
    assert worker_def.mservo == mock_multi_servo
    assert worker_def.move_sec == mock_multi_servo.DEF_MOVE_SEC
    assert worker_def.step_n == mock_multi_servo.DEF_STEP_N
    assert not worker_def.is_alive()

    # 明示的に値を指定する場合
    worker_custom = ThreadWorker(mservo=mock_multi_servo, move_sec=0.5, step_n=50)
    assert worker_custom.move_sec == 0.5
    assert worker_custom.step_n == 50


def test_start_and_end(worker):
    """スレッドが正常に開始・終了できるかテストする。"""
    worker_instance, _ = worker
    assert worker_instance.is_alive()


@pytest.mark.parametrize(
    "cmd_key, cmd_value, expected_method, expected_args_func",
    [
        # move_angle_sync: 全引数指定
        (
            "move_angle_sync",
            {
                "target_angles": [10, 20],
                "move_sec": 0.1,
                "step_n": 10,
            },
            "move_angle_sync",
            lambda w: ([10, 20], 0.1, 10),
        ),
        # move_angle_sync: move_sec, step_nがNone (デフォルト値使用)
        (
            "move_angle_sync",
            {"target_angles": [15, 25], "move_sec": None, "step_n": None},
            "move_angle_sync",
            lambda w: ([15, 25], w.move_sec, w.step_n),
        ),
        # move_angle
        (
            "move_angle",
            {"target_angles": [30, 40]},
            "move_angle",
            lambda w: ([30, 40],),
        ),
        # angles (move_angle_syncのエイリアス)
        (
            "angles",
            {"angles": [50, 60]},
            "move_angle_sync",
            lambda w: ([50, 60], w.move_sec, w.step_n),
        ),
    ],
)
def test_move_commands(
    worker, cmd_key, cmd_value, expected_method, expected_args_func
):
    """各種移動コマンドが正しくmservoのメソッドを呼び出すかテストする。"""
    worker_instance, mock_mservo = worker
    cmd = {"cmd": cmd_key, **cmd_value}

    worker_instance.send(json.dumps(cmd))

    target_method = getattr(mock_mservo, expected_method)
    wait_for_call(target_method)

    expected_args = expected_args_func(worker_instance)
    target_method.assert_called_once_with(*expected_args)


@pytest.mark.parametrize(
    "cmd_dict, expected_attr, expected_value",
    [
        ({"cmd": "move_sec", "sec": 1.5}, "move_sec", 1.5),
        ({"cmd": "step_n", "n": 50}, "step_n", 50),
        ({"cmd": "interval", "sec": 0.5}, "interval_sec", 0.5),
    ],
)
def test_parameter_commands(worker, cmd_dict, expected_attr, expected_value):
    """パラメータ変更コマンドが正しくworkerの属性を更新するかテストする。"""
    worker_instance, _ = worker
    worker_instance.send(json.dumps(cmd_dict))

    # パラメータが変更されるまで待機
    timeout = 1.0
    start_time = time.time()
    while getattr(worker_instance, expected_attr) != expected_value:
        if time.time() - start_time > timeout:
            pytest.fail(f"Attribute '{expected_attr}' was not updated in time.")
        time.sleep(0.01)

    assert getattr(worker_instance, expected_attr) == expected_value


def test_sleep_command(worker, mocker):
    """'sleep'コマンドが正しくtime.sleepを呼び出すかテストする。"""
    worker_instance, _ = worker
    # time.sleepをモック化
    mock_sleep = mocker.patch("piservo0.helper.thread_worker.time.sleep")

    worker_instance.send(json.dumps({"cmd": "sleep", "sec": 1.23}))

    # 呼び出しを待機
    timeout = time.time() + 2
    while time.time() < timeout:
        # 意図した呼び出しがあったか確認
        for c in mock_sleep.call_args_list:
            if c == call(1.23):
                assert True
                return
        time.sleep(0.01)
    
    pytest.fail("time.sleep(1.23) was not called")


def test_interval_sleep(worker, mocker):
    """コマンド実行後のinterval sleepが正しく機能するかテストする。"""
    worker_instance, mock_mservo = worker
    mock_sleep = mocker.patch("piservo0.helper.thread_worker.time.sleep")

    # インターバルを設定
    worker_instance.send(json.dumps({"cmd": "interval", "sec": 0.5}))
    time.sleep(0.1)  # コマンド処理を待つ

    # 動作コマンドを送信
    worker_instance.send(json.dumps({"cmd": "angles", "angles": [10]}))

    # 呼び出しを待機
    timeout = time.time() + 2
    while time.time() < timeout:
        # 意図した呼び出しがあったか確認
        for c in mock_sleep.call_args_list:
            if c == call(0.5):
                assert True
                return
        time.sleep(0.01)

    pytest.fail("time.sleep(0.5) for interval was not called")


def test_invalid_json(worker, mocker):
    """無効なJSON文字列を処理しようとした際のエラーをテストする。"""
    worker_instance, mock_mservo = worker
    mock_log_instance = MagicMock()
    mocker.patch("piservo0.helper.thread_worker.get_logger", return_value=mock_log_instance)
    worker_instance.end()
    worker_instance = ThreadWorker(mservo=mock_mservo, debug=True)
    worker_instance.start()

    worker_instance.send("not a json")
    wait_for_call(mock_log_instance.error)
    mock_log_instance.error.assert_called_once_with(ANY, "JSONDecodeError", ANY)
    mock_mservo.move_angle_sync.assert_not_called()
    worker_instance.end()


def test_no_cmd_key(worker, mocker):
    """'cmd'キーがないコマンドを処理しようとした際のエラーをテストする。"""
    worker_instance, mock_mservo = worker
    mock_log_instance = MagicMock()
    mocker.patch("piservo0.helper.thread_worker.get_logger", return_value=mock_log_instance)
    worker_instance.end()
    worker_instance = ThreadWorker(mservo=mock_mservo, debug=True)
    worker_instance.start()

    worker_instance.send(json.dumps({"no_cmd_key": "value"}))
    wait_for_call(mock_log_instance.error)
    mock_log_instance.error.assert_called_once_with(ANY, "KeyError", ANY)
    mock_mservo.move_angle_sync.assert_not_called()
    worker_instance.end()


def test_unknown_command(worker, mocker):
    """未知のコマンドを処理しようとした際のエラーをテストする。"""
    worker_instance, mock_mservo = worker
    mock_log_instance = MagicMock()
    mocker.patch("piservo0.helper.thread_worker.get_logger", return_value=mock_log_instance)
    worker_instance.end()
    worker_instance = ThreadWorker(mservo=mock_mservo, debug=True)
    worker_instance.start()

    cmd = {"cmd": "unknown_command"}
    worker_instance.send(json.dumps(cmd))
    wait_for_call(mock_log_instance.error)
    mock_log_instance.error.assert_called_once_with("ERROR: %s", cmd)
    mock_mservo.move_angle_sync.assert_not_called()
    worker_instance.end()