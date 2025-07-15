#
# (c) 2025 Yoichi Tanibayashi
#
import json
from .my_logger import get_logger

class ServoConfigManager:
    """サーボの設定ファイル(JSON)を管理するクラス。

    ファイルの読み書きという責務を専門に担う。
    """

    def __init__(self, conf_file, debug=False):
        """ServoConfigManagerのコンストラクタ。

        Args:
            conf_file (str): 設定ファイルのパス。
            debug (bool, optional): デバッグログを有効にするフラグ。
                                    デフォルトはFalse。
        """
        self._log = get_logger(self.__class__.__name__, debug)
        self.conf_file = conf_file
        self._log.debug(f"conf_file={self.conf_file}")

    def read_all_configs(self):
        """設定ファイルからすべてのピンのデータを読み込む。

        Returns:
            list: 読み込んだ設定データのリスト。
                  ファイルが存在しない、または不正な形式の場合は空のリストを返す。
        """
        self._log.debug(f'Reading from {self.conf_file}')
        try:
            with open(self.conf_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self._log.warning(f"Config file not found: {self.conf_file}")
            return []
        except json.JSONDecodeError as e:
            self._log.error(f'Invalid JSON format in {self.conf_file}: {e}')
            return []

    def save_all_configs(self, data):
        """すべてのピンのデータをファイルに書き込む。

        Args:
            data (list): 書き込む設定データのリスト。
        """
        self._log.debug(f'Writing to {self.conf_file}')
        try:
            # ピン番号でソートしてから書き込むと、ファイルが綺麗になる
            sorted_data = sorted(data, key=lambda d: d['pin'])
            with open(self.conf_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self._log.error(f'Failed to write to {self.conf_file}: {e}')

    def get_config(self, pin):
        """指定されたピンの設定を読み込む。

        Args:
            pin (int): GPIOピン番号。

        Returns:
            dict | None: ピンの設定データ。見つからない場合はNoneを返す。
        """
        all_data = self.read_all_configs()
        for pindata in all_data:
            if pindata.get('pin') == pin:
                return pindata
        return None

    def save_config(self, new_pindata):
        """指定されたピンの設定を更新または追加して保存する。

        Args:
            new_pindata (dict): 保存するピンの設定データ。
        """
        pin_to_save = new_pindata['pin']
        all_data = self.read_all_configs()
        
        # 既存のデータを削除し、新しいデータを追加する
        other_pins_data = [p for p in all_data if p.get('pin') != pin_to_save]
        other_pins_data.append(new_pindata)
        
        self.save_all_configs(other_pins_data)
