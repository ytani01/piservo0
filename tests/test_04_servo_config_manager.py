#
# (c) 2025 Yoichi Tanibayashi
#
"""
Test for ServoConfigManager
"""
import json
import pytest
from piservo0.servo_config_manager import ServoConfigManager

TEST_PIN1 = 17
TEST_PIN2 = 27


@pytest.fixture
def config_manager(tmp_path):
    """
    ServoConfigManagerのテスト用フィクスチャ。
    一時的な設定ファイルを使用する。
    """
    conf_file = tmp_path / "test_servo_conf.json"
    manager = ServoConfigManager(str(conf_file), debug=True)
    yield manager, str(conf_file)


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
    assert manager.get_config(TEST_PIN1)["center"] == 1501  # PIN1が消えていない
    assert manager.get_config(TEST_PIN2)["center"] == 1601

    # 3. PIN1のデータを更新
    pin1_data_updated = {"pin": TEST_PIN1, "center": 1599}
    manager.save_config(pin1_data_updated)
    assert manager.get_config(TEST_PIN2)["center"] == 1601  # PIN2が消えていない
    assert manager.get_config(TEST_PIN1)["center"] == 1599  # PIN1が更新されている


def test_read_non_existent_file(tmp_path):
    """
    存在しない設定ファイルを読もうとした場合に空のリストが返るか。
    """
    conf_file = tmp_path / "non_existent.json"
    manager = ServoConfigManager(str(conf_file))
    assert manager.read_all_configs() == []


def test_read_invalid_json(config_manager):
    """
    不正なJSONファイルを読もうとした場合に空のリストが返るか。
    """
    manager, conf_file = config_manager
    with open(conf_file, "w") as f:
        f.write("this is not json")

    assert manager.read_all_configs() == []