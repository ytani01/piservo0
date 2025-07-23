#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for CLI calib command
"""
import pytest
import json
from click.testing import CliRunner
from unittest.mock import patch, call
from piservo0.__main__ import cli  # __main__.pyのcliグループをインポート
from piservo0.servo_config_manager import ServoConfigManager

PIN = 17

@pytest.fixture
def runner():
    """
    Click CLIテスト用のCliRunnerフィクスチャ
    """
    return CliRunner()

@pytest.fixture
def setup_config_file(tmp_path):
    """
    テスト用の設定ファイルを準備するフィクスチャ
    """
    conf_file = tmp_path / "servo_test.json"
    initial_config = [
        {"pin": PIN, "min": 500, "center": 1500, "max": 2500},
    ]
    with open(conf_file, "w") as f:
        json.dump(initial_config, f, indent=2)
    return str(conf_file)

def test_cli_calib_angle_input(runner, mocker_pigpio, setup_config_file):
    """
    CLI calibコマンドが角度入力を正しく処理するかテスト
    """
    pi_mock = mocker_pigpio()
    with patch("builtins.input", side_effect=["10.5", "q"]):
        result = runner.invoke(cli, ["calib", str(PIN), "--conf_file", setup_config_file])

    assert result.exit_code == 0
    assert "angle = 10.5" in result.output
    # 手動でcall_args_listをチェック
    found_call = False
    for c in pi_mock.set_servo_pulsewidth.call_args_list:
        if c.args[0] == PIN and pytest.approx(c.args[1], abs=1) == 1616: # abs=1を追加
            found_call = True
            break
    assert found_call, f"Expected call(PIN, 1616) not found in {pi_mock.set_servo_pulsewidth.call_args_list}"
    pi_mock.stop.assert_called_once()

def test_cli_calib_pulse_input(runner, mocker_pigpio, setup_config_file):
    """
    CLI calibコマンドがパルス幅入力を正しく処理するかテスト
    """
    pi_mock = mocker_pigpio()
    # get_servo_pulsewidthの戻り値を設定
    pi_mock.get_servo_pulsewidth.return_value = 1200
    with patch("builtins.input", side_effect=["1200", "q"]):
        result = runner.invoke(cli, ["calib", str(PIN), "--conf_file", setup_config_file])

    assert result.exit_code == 0
    # CmdCalib.main()の出力は get_pulse() の結果なので、入力された1200を期待
    assert "pulse = 1200" in result.output
    pi_mock.set_servo_pulsewidth.assert_has_calls([
        call(PIN, 0), # 初期化時のoff()
        call(PIN, 1200) # 期待するパルス値
    ], any_order=True)
    pi_mock.stop.assert_called_once()

def test_cli_calib_commands(runner, mocker_pigpio, setup_config_file):
    """
    CLI calibコマンドが各種コマンドを正しく処理するかテスト
    """
    pi_mock = mocker_pigpio()
    # get_servo_pulsewidthの戻り値を設定
    # c, n, x, g, sc, sn, sx コマンドの順に返す値
    pi_mock.get_servo_pulsewidth.side_effect = [1500, 500, 2500, 1500, 1500, 500, 2500] # 7つの値
    commands = ["h", "c", "n", "x", "g", "sc", "sn", "sx", "s", "invalid", "q"] # 's'コマンドを追加
    with patch("builtins.input", side_effect=commands):
        result = runner.invoke(cli, ["calib", str(PIN), "--conf_file", setup_config_file])

    assert result.exit_code == 0
    assert "USAGE" in result.output
    assert "center: pulse=1500" in result.output # 期待するパルス値
    assert "min: pulse=500" in result.output # 期待するパルス値
    assert "max: pulse=2500" in result.output # 期待するパルス値
    assert "pulse = 1500" in result.output # 期待するパルス値
    assert "set center: pulse = 1500" in result.output # 値も含む
    assert "set min: pulse = 500" in result.output # 値も含む
    assert "set max: pulse = 2500" in result.output # 値も含む
    assert "Configuration saved to" in result.output # 's'コマンドの出力
    assert "invalid command" in result.output # 'invalid'コマンドに対するエラーメッセージ
    pi_mock.stop.assert_called_once()

def test_cli_calib_save_config(runner, mocker_pigpio, tmp_path):
    """
    CLI calibコマンドが設定を保存できるかテスト
    """
    conf_file = tmp_path / "save_test.json"
    # 初期設定は空で開始
    with open(conf_file, "w") as f:
        json.dump([], f)

    pi_mock = mocker_pigpio()
    # get_servo_pulsewidthの戻り値を設定
    pi_mock.get_servo_pulsewidth.side_effect = [500, 500, 1500, 1500, 2500, 2500] # 6つの値
    # min, center, max を設定し、保存して終了
    with patch("builtins.input", side_effect=["500", "sn", "1500", "sc", "2500", "sx", "s", "q"]): # 入力シーケンスを修正
        result = runner.invoke(cli, ["calib", str(PIN), "--conf_file", str(conf_file)])

    assert result.exit_code == 0
    assert "Configuration saved to" in result.output

    # 保存されたファイルの内容を検証
    with open(conf_file, "r") as f:
        saved_config = json.load(f)

    assert len(saved_config) == 1
    assert saved_config[0]["pin"] == PIN
    assert saved_config[0]["min"] == 500
    assert saved_config[0]["center"] == 1500
    assert saved_config[0]["max"] == 2500
    pi_mock.stop.assert_called_once()

def test_cli_calib_load_config(runner, mocker_pigpio, tmp_path):
    """
    CLI calibコマンドが既存の設定をロードできるかテスト
    """
    conf_file = tmp_path / "load_test.json"
    initial_config = [
        {"pin": PIN, "min": 600, "center": 1600, "max": 2600},
    ]
    with open(conf_file, "w") as f:
        json.dump(initial_config, f, indent=2)

    pi_mock = mocker_pigpio()
    # 設定をロードし、'g'コマンドで確認して終了
    with patch("builtins.input", side_effect=["g", "q"]):
        result = runner.invoke(cli, ["calib", str(PIN), "--conf_file", str(conf_file)])

    assert result.exit_code == 0
    assert "min=600" in result.output
    assert "center=1600" in result.output
    assert "max=2600" in result.output
    pi_mock.stop.assert_called_once()
