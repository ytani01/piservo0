#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for ThreadMultiServo (Composition-based design)
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from piservo0 import ThreadMultiServo, MultiServo


TEST_PINS = [17, 27, 22, 23]


@pytest.fixture
def mock_worker(mocker):
    """
    ThreadWorkerのモックを作成し、
    ThreadMultiServoのコンストラクタで返されるように設定するフィクスチャ。
    """
    mock_worker_instance = MagicMock()
    # patchの対象は、テスト対象のモジュールがインポートしている場所
    mocker.patch(
        "piservo0.thread_multi_servo.ThreadWorker",
        return_value=mock_worker_instance,
    )
    yield mock_worker_instance


@pytest.fixture
def tms_instance(mocker_pigpio, mock_worker):
    """
    ThreadMultiServoのテスト用インスタンスを作成するフィクスチャ。
    pigpioとThreadWorkerの両方がモック化される。
    """
    pi = mocker_pigpio()
    # first_move=Falseにして、初期化時のサーボ動作を抑制
    # conf_fileは指定せず、デフォルトの挙動をテストする
    tms = ThreadMultiServo(
        pi, TEST_PINS, first_move=False, debug=True
    )
    yield tms
    # テスト終了時にendを呼んでおく
    tms.end()


def test_constructor(tms_instance, mock_worker):
    """
    コンストラクタでThreadWorkerが正しく初期化・開始されるかテストする。
    """
    # 親クラスがMultiServoであることを確認
    assert isinstance(tms_instance, MultiServo)

    # ThreadWorkerのコンストラクタが期待通りに呼ばれたか
    from piservo0.thread_multi_servo import ThreadWorker

    ThreadWorker.assert_called_once_with(mservo=tms_instance, debug=True)

    # workerのstartメソッドが呼ばれたか
    mock_worker.start.assert_called_once()


def test_end(tms_instance, mock_worker):
    """
    end()メソッドがworkerのend()を呼び出し、親のoff()も呼び出すかテストする。
    """
    # 親のoffメソッドをモック化して呼び出しを監視
    with patch.object(MultiServo, "off") as mock_super_off:
        tms_instance.end()
        mock_worker.end.assert_called_once()
        mock_super_off.assert_called_once()


def test_move_angle_sync_async(tms_instance, mock_worker):
    """
    move_angle_sync_asyncが正しいコマンド群をworkerに送信するかテストする。
    """
    target_angles = [10, 20, 30, 40]
    sec = 0.5
    step_n = 20

    tms_instance.move_angle_sync_async(
        target_angles, move_sec=sec, step_n=step_n
    )

    # パラメータ設定コマンドがJSON形式で送信されたか
    mock_worker.send.assert_any_call(json.dumps({"cmd": "move_sec", "sec": sec}))
    mock_worker.send.assert_any_call(json.dumps({"cmd": "step_n", "n": step_n}))

    # 角度設定コマンドがJSON形式で送信されたか
    mock_worker.send.assert_any_call(
        json.dumps({"cmd": "angles", "angles": target_angles})
    )


def test_move_angle_async(tms_instance, mocker):
    """
    move_angle_asyncがstep_n=1でmove_angle_sync_asyncを呼び出すかテストする。
    """
    # tms_instance自身のメソッドをモック化
    mock_sync_async = mocker.patch.object(
        tms_instance, "move_angle_sync_async"
    )

    target_angles = [50, 60, 70, 80]
    tms_instance.move_angle_async(target_angles, move_sec=0.1)

    # 期待される引数で呼び出されたか
    mock_sync_async.assert_called_once_with(
        target_angles, move_sec=0.1, step_n=1
    )


@pytest.mark.parametrize(
    "method_name, method_args, expected_cmd",
    [
        (
            "set_move_sec_async",
            (1.23,),
            {"cmd": "move_sec", "sec": 1.23},
        ),
        ("set_step_n_async", (55,), {"cmd": "step_n", "n": 55}),
        (
            "set_interval_async",
            (0.99,),
            {"cmd": "interval", "sec": 0.99},
        ),
        ("sleep_async", (2.5,), {"cmd": "sleep", "sec": 2.5}),
    ],
)
def test_simple_async_commands(
    tms_instance, mock_worker, method_name, method_args, expected_cmd
):
    """
    単純な非同期コマンドが正しいJSONをworkerに送信するかテストする。
    """
    # テスト対象のメソッドを取得して実行
    method_to_call = getattr(tms_instance, method_name)
    method_to_call(*method_args)

    # 正しいJSON文字列でsendが呼ばれたか
    mock_worker.send.assert_called_once_with(json.dumps(expected_cmd))
