#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for CLI servo command
"""
import pytest
from click.testing import CliRunner
from unittest.mock import call
from piservo0.__main__ import cli  # __main__.pyのcliグループをインポート

@pytest.fixture
def runner():
    """
    Click CLIテスト用のCliRunnerフィクスチャ
    """
    return CliRunner()

def test_cli_servo_numeric_pulse(runner, mocker_pigpio):
    """
    CLI servoコマンドが数値パルス幅を正しく処理するかテスト
    """
    pi_mock = mocker_pigpio()
    result = runner.invoke(cli, ["servo", "17", "1500"])

    assert result.exit_code == 0
    assert "bye!" in result.output
    # 初期化時のoff()と、move_pulseの呼び出しを確認 (順序は問わない)
    pi_mock.set_servo_pulsewidth.assert_has_calls([
        call(17, 0), # 初期化時のoff()
        call(17, 1500) # 期待するパルス値
    ], any_order=True)
    pi_mock.stop.assert_called_once()

def test_cli_servo_keyword_pulse(runner, mocker_pigpio):
    """
    CLI servoコマンドがキーワードパルス幅(min, max, center)を正しく処理するかテスト
    """
    pi_mock = mocker_pigpio()

    # min
    result = runner.invoke(cli, ["servo", "17", "min"])
    assert result.exit_code == 0
    assert "bye!" in result.output
    pi_mock.set_servo_pulsewidth.assert_has_calls([
        call(17, 0), # 初期化時のoff()
        call(17, 500) # PiServo.MIN
    ], any_order=True)
    pi_mock.stop.assert_called_once()
    pi_mock.reset_mock() # モックの状態をリセット

    # max
    result = runner.invoke(cli, ["servo", "17", "max"])
    assert result.exit_code == 0
    assert "bye!" in result.output
    pi_mock.set_servo_pulsewidth.assert_has_calls([
        call(17, 0), # 初期化時のoff()
        call(17, 2500) # PiServo.MAX
    ], any_order=True)
    pi_mock.stop.assert_called_once()
    pi_mock.reset_mock()

    # center
    result = runner.invoke(cli, ["servo", "17", "center"])
    assert result.exit_code == 0
    assert "bye!" in result.output
    pi_mock.set_servo_pulsewidth.assert_has_calls([
        call(17, 0), # 初期化時のoff()
        call(17, 1500) # PiServo.CENTER
    ], any_order=True)
    pi_mock.stop.assert_called_once()
    pi_mock.reset_mock()

def test_cli_servo_invalid_pulse(runner, mocker_pigpio):
    """
    CLI servoコマンドが無効なパルス幅を処理したときにエラーを出すかテスト
    """
    pi_mock = mocker_pigpio()
    result = runner.invoke(cli, ["servo", "17", "invalid"])

    assert result.exit_code == 0 # エラー終了コードは0になる
    assert "invalid pulse string" in result.output # 警告メッセージを確認
    assert "invalid value. do nothing" in result.output # エラーメッセージを確認
    pi_mock.set_servo_pulsewidth.assert_called_once_with(17, 0) # 初期化時のoff()のみ
    pi_mock.stop.assert_called_once() # エラー時でもpi.stop()は呼ばれる

def test_cli_servo_out_of_range_pulse(runner, mocker_pigpio):
    """
    CLI servoコマンドが範囲外の数値パルス幅を処理したときにエラーを出すかテスト
    """
    pi_mock = mocker_pigpio()

    # 最小値未満
    result = runner.invoke(cli, ["servo", "17", "499"])
    assert result.exit_code == 0
    assert "invalid value. do nothing" in result.output
    pi_mock.set_servo_pulsewidth.assert_called_once_with(17, 0) # 初期化時のoff()のみ
    pi_mock.stop.assert_called_once()
    pi_mock.reset_mock()

    # 最大値超え
    result = runner.invoke(cli, ["servo", "17", "2501"])
    assert result.exit_code == 0
    assert "invalid value. do nothing" in result.output
    pi_mock.set_servo_pulsewidth.assert_called_once_with(17, 0) # 初期化時のoff()のみ
    pi_mock.stop.assert_called_once()
    pi_mock.reset_mock()

def test_cli_servo_duration(runner, mocker_pigpio):
    """
    CLI servoコマンドがduration引数を正しく処理するかテスト
    """
    pi_mock = mocker_pigpio()
    result = runner.invoke(cli, ["servo", "17", "1500", "--sec", "0.5"])

    assert result.exit_code == 0
    assert "bye!" in result.output
    pi_mock.set_servo_pulsewidth.assert_has_calls([
        call(17, 0), # 初期化時のoff()
        call(17, 1500) # 期待するパルス値
    ], any_order=True)
    # time.sleepのモックはconftest.pyで対応済みなので、ここでは直接検証しない
    pi_mock.stop.assert_called_once()