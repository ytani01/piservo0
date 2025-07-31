#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for ServoConfigManager
"""
import json
import os
from pathlib import Path

import pytest

from piservo0.utils.servo_config_manager import ServoConfigManager

TEST_PIN1 = 17
TEST_PIN2 = 27
TEST_CONF_FILENAME = "test_servo_conf.json"


@pytest.fixture
def setup_test_env(tmp_path, monkeypatch):
    """
    テスト用の環境をセットアップするフィクスチャ。
    一時的なカレントディレクトリとホームディレクトリを作成し、
    テスト終了後にもとに戻す。
    """
    # 一時的なディレクトリを作成
    test_cwd = tmp_path / "cwd"
    test_home = tmp_path / "home"
    test_cwd.mkdir()
    test_home.mkdir()

    # Path.home() と os.getcwd() をモンキーパッチで差し替え
    monkeypatch.setattr(Path, "home", lambda: test_home)
    monkeypatch.setattr(os, "getcwd", lambda: str(test_cwd))

    # テスト中は作成したカレントディレクトリに移動
    monkeypatch.chdir(test_cwd)

    # 各ディレクトリのパスをyieldで返す
    yield {
        "cwd": test_cwd,
        "home": test_home,
    }


# ======================================================================
# Test for file finding logic
# ======================================================================
def test_find_conf_in_current_dir(setup_test_env):
    """
    カレントディレクトリに設定ファイルが存在する場合、それが使われるか。
    """
    # セットアップ
    cwd_path = setup_test_env["cwd"]
    conf_path = cwd_path / TEST_CONF_FILENAME
    conf_path.touch()  # 空のファイルを作成

    # 実行
    manager = ServoConfigManager(TEST_CONF_FILENAME, debug=True)

    # 検証
    assert Path(manager.conf_file).resolve() == conf_path.resolve()


def test_find_conf_in_home_dir(setup_test_env):
    """
    カレントにはなく、ホームディレクトリに設定ファイルが存在する場合、それが使われるか。
    """
    # セットアップ
    home_path = setup_test_env["home"]
    conf_path = home_path / TEST_CONF_FILENAME
    conf_path.touch()

    # 実行
    manager = ServoConfigManager(TEST_CONF_FILENAME, debug=True)

    # 検証
    assert Path(manager.conf_file).resolve() == conf_path.resolve()


def test_conf_not_found_defaults_to_current_dir(setup_test_env):
    """
    どこにも設定ファイルが存在しない場合、
    カレントディレクトリにデフォルトのパスが設定されるか。
    """
    # セットアップ
    cwd_path = setup_test_env["cwd"]
    expected_path = cwd_path / TEST_CONF_FILENAME

    # 実行
    manager = ServoConfigManager(TEST_CONF_FILENAME, debug=True)

    # 検証
    assert Path(manager.conf_file).resolve() == expected_path.resolve()
    # 実際にファイルがまだ作成されていないことも確認
    assert not expected_path.exists()


def test_absolute_path_is_used_directly(setup_test_env):
    """
    絶対パスで設定ファイルが指定された場合、検索ロジックを無視してそのパスが使われるか。
    """
    # セットアップ
    # 通常の検索パスとは異なる場所にファイルを作成
    special_dir = setup_test_env["cwd"] / "special"
    special_dir.mkdir()
    conf_path = special_dir / "my_special_config.json"
    conf_path.touch()

    # 実行
    manager = ServoConfigManager(str(conf_path), debug=True)

    # 検証
    assert Path(manager.conf_file).resolve() == conf_path.resolve()


def test_search_priority(setup_test_env):
    """
    カレントとホームの両方にファイルがある場合、カレントが優先されるか。
    """
    # セットアップ
    cwd_path = setup_test_env["cwd"]
    home_path = setup_test_env["home"]

    # 両方の場所にファイルを作成
    cwd_conf_path = cwd_path / TEST_CONF_FILENAME
    home_conf_path = home_path / TEST_CONF_FILENAME
    cwd_conf_path.touch()
    home_conf_path.touch()

    # 実行
    manager = ServoConfigManager(TEST_CONF_FILENAME, debug=True)

    # 検証
    assert Path(manager.conf_file).resolve() == cwd_conf_path.resolve()


# ======================================================================
# Test for config manipulation methods
# ======================================================================
@pytest.fixture
def config_manager(setup_test_env):
    """
    ServoConfigManagerのテスト用フィクスチャ。
    ファイル名のみで初期化することで、ファイル検索ロジックもテストする。
    """
    # ServoConfigManagerをファイル名で初期化
    manager = ServoConfigManager(TEST_CONF_FILENAME, debug=True)

    # managerと、期待される設定ファイルのフルパスを渡す
    yield manager, str(setup_test_env["cwd"] / TEST_CONF_FILENAME)


def test_read_write_all_configs(config_manager):
    """
    設定の書き込みと読み込みが正しく行われるか。
    """
    manager, conf_file = config_manager
    test_data = [
        {"pin": TEST_PIN1, "min": 600, "center": 1500, "max": 2400},
        {"pin": TEST_PIN2, "min": 700, "center": 1600, "max": 2500},
    ]

    manager.save_all_configs(test_data)

    # ファイルが書き込まれたか
    with open(conf_file, "r") as f:
        saved_data = json.load(f)
    # pinでソートされて保存されることを確認
    assert saved_data[0]["pin"] == TEST_PIN1
    assert saved_data[1]["pin"] == TEST_PIN2

    # 読み込んだデータが一致するか
    loaded_data = manager.read_all_configs()
    assert loaded_data == saved_data


def test_get_config(config_manager):
    """
    特定のピンの設定を正しく取得できるか。
    """
    manager, _ = config_manager
    test_data = [
        {"pin": TEST_PIN1, "center": 1550},
        {"pin": TEST_PIN2, "center": 1650},
    ]
    manager.save_all_configs(test_data)

    config1 = manager.get_config(TEST_PIN1)
    assert config1["center"] == 1550

    config2 = manager.get_config(TEST_PIN2)
    assert config2["center"] == 1650

    # 存在しないピン
    config_none = manager.get_config(99)
    assert config_none is None


def test_save_config_add_and_update(config_manager):
    """
    save_configで設定の追加と更新が正しく行われるか。
    """
    manager, _ = config_manager

    # 1. PIN1のデータを追加
    pin1_data = {"pin": TEST_PIN1, "center": 1501}
    manager.save_config(pin1_data)
    assert manager.get_config(TEST_PIN1)["center"] == 1501

    # 2. PIN2のデータを追加
    pin2_data = {"pin": TEST_PIN2, "center": 1601}
    manager.save_config(pin2_data)
    # PIN1が消えていない
    assert manager.get_config(TEST_PIN1)["center"] == 1501
    assert manager.get_config(TEST_PIN2)["center"] == 1601

    # 3. PIN1のデータを更新
    pin1_data_updated = {"pin": TEST_PIN1, "center": 1599}
    manager.save_config(pin1_data_updated)
    # PIN2が消えていない
    assert manager.get_config(TEST_PIN2)["center"] == 1601
    # PIN1が更新されている
    assert manager.get_config(TEST_PIN1)["center"] == 1599


def test_read_invalid_json(config_manager):
    """
    不正なJSONファイルを読もうとした場合に空のリストが返るか。
    """
    manager, conf_file = config_manager
    with open(conf_file, "w") as f:
        f.write("this is not json")

    assert manager.read_all_configs() == []