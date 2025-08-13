#
# (c) 2025 Yoichi Tanibayashi
#
import json
import os
from pathlib import Path

from .my_logger import get_logger


class ServoConfigManager:
    """サーボの設定ファイル(JSON)を管理するクラス。

    ファイルの読み書きという責務を専門に担う。
    """

    def __init__(self, conf_file, debug=False):
        """ServoConfigManagerのコンストラクタ。

        Args:
            conf_file (str): 設定ファイルのパス。
            debug (bool, optional): debug flag.
        """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)

        self.conf_file = self._find_conf_file(conf_file)
        self.__log.debug("found conf_file: %s", self.conf_file)

    def _find_conf_file(self, conf_file: str) -> str:
        """設定ファイルを検索し、有効なパスを返す。(プライベートメソッド)

        1. カレントディレクトリ
        2. ホームディレクトリ
        3. /etc/

        の順で探し、最初に見つかったファイルのパスを返す。
        どこにも見つからない場合は、カレントディレクトリのパスを返す。

        Args:
            conf_file (str): 設定ファイル名。

        Returns:
            str: 有効な設定ファイルのパス。
        """
        # 絶対パスが指定された場合は、それをそのまま使う
        if os.path.dirname(conf_file):
            return os.path.abspath(conf_file)

        # 検索パスのリスト
        search_paths = [
            Path.cwd() / conf_file,
            Path.home() / conf_file,
            Path("/etc") / conf_file,
        ]

        self.__log.debug("Searching for %s in:", conf_file)
        for path in search_paths:
            self.__log.debug("  - %s", path)
            if path.is_file():
                self.__log.debug("Found config file at: %s", path)
                return str(path)

        # 見つからなかった場合はカレントディレクトリに作成する
        default_path = Path.cwd() / conf_file
        self.__log.warning(
            "Config file not found. Defaulting to: %s", default_path
        )
        return str(default_path)

    def read_all_configs(self):
        """設定ファイルからすべてのピンのデータを読み込む。

        Returns:
            list: 読み込んだ設定データのリスト。
                  ファイルが存在しない、または不正な形式の場合は空のリストを返す。
        """
        self.__log.debug("Reading from %s", self.conf_file)
        try:
            with open(self.conf_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.__log.warning("Config file not found: %s", self.conf_file)
            return []
        except json.JSONDecodeError as e:
            self.__log.error(
                "Invalid JSON format in %s: %s", self.conf_file, e
            )
            return []

    def save_all_configs(self, data):
        """すべてのピンのデータをファイルに書き込む。

        Args:
            data (list): 書き込む設定データのリスト。
        """
        self.__log.debug("Writing to %s", self.conf_file)
        try:
            # ピン番号でソートしてから書き込むと、ファイルが綺麗になる
            sorted_data = sorted(data, key=lambda d: d["pin"])
            with open(self.conf_file, "w", encoding="utf-8") as f:
                json.dump(sorted_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.__log.error("Failed to write to %s: %s", self.conf_file, e)

    def get_config(self, pin):
        """指定されたピンの設定を読み込む。

        Args:
            pin (int): GPIOピン番号。

        Returns:
            dict | None: ピンの設定データ。見つからない場合はNoneを返す。
        """
        all_data = self.read_all_configs()
        for pindata in all_data:
            if pindata.get("pin") == pin:
                return pindata
        return None

    def save_config(self, new_pindata):
        """指定されたピンの設定を更新または追加して保存する。

        Args:
            new_pindata (dict): 保存するピンの設定データ。
        """
        pin_to_save = new_pindata["pin"]
        all_data = self.read_all_configs()

        # 既存のデータを削除し、新しいデータを追加する
        other_pins_data = [p for p in all_data if p.get("pin") != pin_to_save]
        other_pins_data.append(new_pindata)

        self.save_all_configs(other_pins_data)
