#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for ThreadMultiServo
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from piservo0 import ThreadMultiServo, CalibrableServo


TEST_PINS = [17, 27, 22, 23]


@pytest.fixture
def mock_mservo(mocker):
    """MultiServoのモックを作成するフィクスチャ"""
    mock_instance = MagicMock()
    # patchの対象は、テスト対象のモジュールがインポートしている場所
    mocker.patch(
        "piservo0.thread_multi_servo.MultiServo", return_value=mock_instance
    )
    return mock_instance


@pytest.fixture
def mock_worker(mocker):
    """ThreadWorkerのモックを作成するフィクスチャ"""
    mock_instance = MagicMock()
    mocker.patch(
        "piservo0.thread_multi_servo.ThreadWorker", return_value=mock_instance
    )
    return mock_instance


@pytest.fixture
def tms_instance(mocker_pigpio, mock_mservo, mock_worker):
    """
    ThreadMultiServoのテスト用インスタンスを作成するフィクスチャ。
    pigpio, MultiServo, ThreadWorkerがモック化される。
    """
    pi = mocker_pigpio()
    tms = ThreadMultiServo(pi, TEST_PINS, first_move=False, debug=True)
    yield tms, pi
    tms.end()


def test_constructor(tms_instance, mock_mservo, mock_worker):
    """
    コンストラクタでMultiServoとThreadWorkerが正しく初期化されるかテストする。
    """
    tms, pi = tms_instance
    from piservo0.thread_multi_servo import MultiServo, ThreadWorker

    # MultiServoが期待通りに呼ばれたか
    MultiServo.assert_called_once_with(
        pi, TEST_PINS, False, CalibrableServo.DEF_CONF_FILE, True
    )

    # ThreadWorkerが期待通りに呼ばれたか
    ThreadWorker.assert_called_once_with(mservo=mock_mservo, debug=True)

    # workerのstartメソッドが呼ばれたか
    mock_worker.start.assert_called_once()


def test_end(tms_instance, mock_mservo, mock_worker):
    """
    end()メソッドがworkerとmservoのメソッドを正しく呼び出すかテストする。
    """
    tms, _ = tms_instance
    tms.end()
    mock_worker.end.assert_called_once()
    mock_worker.join.assert_called_once()
    mock_mservo.off.assert_called_once()


def test_move_angle(tms_instance, mock_worker):
    """
    move_angleが正しいコマンドをworkerに送信するかテストする。
    """
    tms, _ = tms_instance
    target_angles = [10, 20, 30, 40]
    tms.move_angle(target_angles)

    expected_cmd = {"cmd": "move_angle", "target_angles": target_angles}
    mock_worker.send.assert_called_once_with(json.dumps(expected_cmd))


def test_move_angle_sync(tms_instance, mock_worker):
    """
    move_angle_syncが正しいコマンドをworkerに送信するかテストする。
    """
    tms, _ = tms_instance
    target_angles = [10, 20, 30, 40]
    sec = 0.5
    step_n = 20

    tms.move_angle_sync(target_angles, move_sec=sec, step_n=step_n)

    expected_cmd = {
        "cmd": "move_angle_sync",
        "target_angles": target_angles,
        "move_sec": sec,
        "step_n": step_n,
    }
    mock_worker.send.assert_called_once_with(json.dumps(expected_cmd))


@pytest.mark.parametrize(
    "method_name, method_args, expected_cmd",
    [
        ("set_move_sec", (1.23,), {"cmd": "move_sec", "sec": 1.23}),
        ("set_step_n", (55,), {"cmd": "step_n", "n": 55}),
        ("set_interval", (0.99,), {"cmd": "interval", "sec": 0.99}),
        ("sleep", (2.5,), {"cmd": "sleep", "sec": 2.5}),
    ],
)
def test_simple_commands(
    tms_instance, mock_worker, method_name, method_args, expected_cmd
):
    """
    単純なコマンドが正しいJSONをworkerに送信するかテストする。
    """
    tms, _ = tms_instance
    method_to_call = getattr(tms, method_name)
    method_to_call(*method_args)
    mock_worker.send.assert_called_once_with(json.dumps(expected_cmd))


def test_get_methods(tms_instance, mock_mservo):
    """
    get_pulseとget_angleが内包するmservoのメソッドを呼び出すかテストする。
    """
    tms, _ = tms_instance
    mock_mservo.get_pulse.return_value = [1500] * 4
    mock_mservo.get_angle.return_value = [0.0] * 4

    assert tms.get_pulse() == [1500] * 4
    mock_mservo.get_pulse.assert_called_once()

    assert tms.get_angle() == [0.0] * 4
    mock_mservo.get_angle.assert_called_once()
