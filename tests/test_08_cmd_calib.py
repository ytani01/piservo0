#
# (c) 2025 Yoichi Tanibayashi
#
import sys
import pytest
import pigpio
import time
import os
import json
from unittest.mock import patch
from piservo0.cmd_calib import CmdCalib
from piservo0.piservo import PiServo

SLEEP_SEC = 0.5

def check_pigpiod():
    """Check if pigpiod is running"""
    try:
        pi = pigpio.pi()
        if not pi.connected:
            return False
        pi.stop()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not check_pigpiod(), reason="pigpiod is not running")


@pytest.fixture
def calib_app():
    """CmdCalibのテスト用インスタンス"""
    test_conf_file = './servo_test.json'
    test_pin = 17

    # テスト用の設定ファイルを初期化
    initial_config = [
        {"pin": test_pin, "min": 500, "center": 1500, "max": 2500},
        {"pin": 17, "min": 2500, "center": 2500, "max": 2500} # 他のピンは現状維持
    ]
    with open(test_conf_file, 'w') as f:
        json.dump(initial_config, f, indent=2)

    pi = pigpio.pi() # pigpio.pi()インスタンスをフィクスチャで管理
    if not pi.connected:
        pytest.fail("pigpio daemon not connected.")

    app = CmdCalib(pi, test_pin, test_conf_file, debug=True)
    # CmdCalibの内部でpiインスタンスが作成されるため、ここでは渡さない
    # app.pi = pi # これをすると二重管理になる

    yield app

    # テスト後のクリーンアップ
    app.end() 
    pi.stop() # フィクスチャで作成したpiインスタンスを停止
    if os.path.exists(test_conf_file):
        os.remove(test_conf_file)


def test_cmd_calib_init_ok(calib_app):
    """CmdCalib.__init__()"""
    assert calib_app.pin == 17
    assert calib_app.conf_file == './servo_test.json'
    assert calib_app.pi.connected


def test_cmd_calib_main_angle(calib_app, mocker, capsys):
    """CmdCalib.main() angle"""
    mocker.patch('builtins.input', side_effect=['10.5', 'q'])

    mock_ctx = mocker.MagicMock()
    mock_ctx.command.name = 'calib'

    calib_app.main(mock_ctx)

    captured = capsys.readouterr()
    assert 'angle = 10.5' in captured.out


@pytest.mark.parametrize(('input_str', 'expected_output_str', 'expect_error_log'), [
    # 角度のテスト
    ('0', ' angle = 0.0, pulse=', False),
    ('-40', ' angle = -40.0, pulse=', False),
    ('60', ' angle = 60.0, pulse=', False),
    ('-90', ' angle = -90.0, pulse=', False),
    ('90', ' angle = 90.0, pulse=', False),
    ('-100', ': out of range', True), # 範囲外(下)
    ('100', ': out of range', True),  # 範囲外(上)
    # パルスのテスト
    ('1000', ' pulse = 1000', False),
    ('1500', ' pulse = 1500', False),
    ('2000', ' pulse = 2000', False),
    ('300', ': out of range', True),  # 範囲外(下)
    ('3000', ': out of range', True), # 範囲外(上)
    # コマンドのテスト
    ('n', ' min: pulse=', False),
    ('x', ' max: pulse=', False),
    ('c', ' center: pulse=', False),
])
def test_cmd_calib_main_input(calib_app, mocker, capsys, input_str, expected_output_str, expect_error_log):
    """CmdCalib.main() input (angle and pulse)"""
    mocker.patch('builtins.input', side_effect=[input_str, 'q'])
    mocker.patch.object(calib_app._log, 'error', side_effect=lambda msg, *args: print(msg % args, file=sys.stderr)) # エラーログをstderrに出力するようにモック

    mock_ctx = mocker.MagicMock()
    mock_ctx.command.name = 'calib'

    calib_app.main(mock_ctx)

    captured = capsys.readouterr()

    if expect_error_log:
        calib_app._log.error.assert_called_once_with('%s: out of range', float(input_str))
        assert f'{float(input_str)}{expected_output_str}' in captured.err
        assert expected_output_str not in captured.out # 範囲外の場合は出力されない
    else:
        calib_app._log.error.assert_not_called()
        assert expected_output_str in captured.out
        assert captured.err == ''

    # 最終的なサーボのパルス値が期待通りかを確認
    if input_str == 'c':
        expected_pulse_val = calib_app.servo.pulse_center
    elif input_str == 'n':
        expected_pulse_val = calib_app.servo.pulse_min
    elif input_str == 'x':
        expected_pulse_val = calib_app.servo.pulse_max
    elif 'angle' in expected_output_str:
        expected_pulse_val = calib_app.servo.deg2pulse(float(input_str))
    elif 'pulse' in expected_output_str:
        expected_pulse_val = int(input_str)
    else: # エラーケースの場合、パルス値は変わらないはず
        expected_pulse_val = calib_app.servo.get_pulse() # 初期値か、直前の値

    assert calib_app.servo.get_pulse() == expected_pulse_val
    time.sleep(SLEEP_SEC) # 目視確認のための待機


def test_cmd_calib_main_commands(calib_app, mocker, capsys):
    """CmdCalib.main() commands"""
    commands = [
        'h', 'c', 'n', 'x', 'g', 'sc', 'sn', 'sx', 'invalid', 'q'
    ]
    mocker.patch('builtins.input', side_effect=commands)
    mocker.patch('time.sleep', return_value=None)

    mock_ctx = mocker.MagicMock()
    mock_ctx.command.name = 'calib'

    mocker.patch.object(calib_app._log, 'error')
    calib_app.main(mock_ctx)

    calib_app._log.error.assert_called_once_with('%s: invalid command', 'invalid')

    captured = capsys.readouterr()
    assert 'USAGE' in captured.out
    assert 'center: pulse=' in captured.out
    assert 'min: pulse=' in captured.out
    assert 'max: pulse=' in captured.out
    assert 'pulse =' in captured.out
    assert 'set center: pulse =' in captured.out
    assert 'set min: pulse =' in captured.out
    assert 'set max: pulse =' in captured.out
