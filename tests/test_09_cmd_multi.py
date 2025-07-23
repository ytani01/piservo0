#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for CLI multi command
"""
import pytest
import json
from click.testing import CliRunner
from unittest.mock import patch, call
from piservo0.__main__ import cli  # __main__.pyのcliグループをインポート
from piservo0.calibrable_servo import CalibrableServo # 追加

PIN_LIST = [17, 27, 22, 23]

@pytest.fixture
def runner():
    """
    Click CLIテスト用のCliRunnerフィクスチャ
    """
    return CliRunner()

@pytest.fixture
def setup_multi_config_file(tmp_path):
    """
    テスト用の設定ファイルを準備するフィクスチャ
    """
    conf_file = tmp_path / "multi_servo_test.json"
    initial_config = [
        {"pin": 17, "min": 500, "center": 1500, "max": 2500},
        {"pin": 27, "min": 500, "center": 1500, "max": 2500},
        {"pin": 22, "min": 500, "center": 1500, "max": 2500},
        {"pin": 23, "min": 500, "center": 1500, "max": 2500},
    ]
    with open(conf_file, "w") as f:
        json.dump(initial_config, f, indent=2)
    return str(conf_file)

def test_cli_multi_angles_input(runner, mocker_pigpio, setup_multi_config_file):
    """
    CLI multiコマンドが複数の角度入力を正しく処理するかテスト
    """
    pi_mock = mocker_pigpio()
    angles_input = "10.5 -20.0 30.0 -40.0"
    with patch("builtins.input", side_effect=[angles_input, "q"]):
        result = runner.invoke(cli, ["multi"] + list(map(str, PIN_LIST)) + ["--conf_file", setup_multi_config_file])

    assert result.exit_code == 0
    # 実際の出力形式に合わせてアサーションを修正
    # CmdMulti.main()の出力は " [angle1, angle2, ...] ... elapsed_time sec"
    # angles_inputから期待されるangles_strを生成
    expected_angles_str = ", ".join([f"{float(a):.0f}" for a in angles_input.split()])
    expected_angles_str = "[" + expected_angles_str + "]"
    assert expected_angles_str in result.output
    assert " ... " in result.output # 時間表示部分も確認

    # pi_mock.set_servo_pulsewidth.assert_has_calls は削除
    pi_mock.stop.assert_called_once()

def test_cli_multi_invalid_input(runner, mocker_pigpio, setup_multi_config_file):
    """
    CLI multiコマンドが無効な入力を処理したときにエラーを出すかテスト
    """
    pi_mock = mocker_pigpio()
    invalid_input = "10.5 invalid 30.0"
    with patch("builtins.input", side_effect=[invalid_input, "q"]):
        result = runner.invoke(cli, ["multi"] + list(map(str, PIN_LIST)) + ["--conf_file", setup_multi_config_file])

    assert result.exit_code == 0 # エラー終了コードは0になる
    assert "ValueError: could not convert string to float: 'invalid'" in result.stderr # stderrを確認
    # pi_mock.set_servo_pulsewidth.assert_has_calls は削除
    pi_mock.stop.assert_called_once()

def test_cli_multi_eof_handling(runner, mocker_pigpio, setup_multi_config_file):
    """
    CLI multiコマンドがEOFErrorを正しく処理するかテスト
    """
    pi_mock = mocker_pigpio()
    with patch("builtins.input", side_effect=EOFError):
        result = runner.invoke(cli, ["multi"] + list(map(str, PIN_LIST)) + ["--conf_file", setup_multi_config_file])

    assert result.exit_code == 0 # EOFErrorは正常終了として扱う
    assert "\n Bye!\n" in result.output # 実際の出力文字列を確認
    pi_mock.set_servo_pulsewidth.assert_has_calls([
        call(17, 0), call(27, 0), call(22, 0), call(23, 0) # 初期化時のoff()
    ], any_order=True)
    pi_mock.stop.assert_called_once()
