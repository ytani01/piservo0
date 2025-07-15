#
# (c) 2025 Yoichi Tanibayashi
#
import json
from .my_logger import get_logger
from .piservo import PiServo


class CalibrableServo(PiServo):
    """PiServoを拡張し、キャリブレーション機能を追加したクラス。

    JSONファイルから各サーボモーターの最小・最大・中央位置のパルス幅を読み込み、
    設定を永続化できる。
    これにより、個々のサーボモーターの物理的な特性に合わせた微調整が可能。

    Attributes:
        DEF_CONF_FILE (str): デフォルトの設定ファイル名。
        conf_file (str): 使用する設定ファイルへのパス。
        center (int): キャリブレーション後の中央位置のパルス幅。
        min (int): キャリブレーション後の最小位置のパルス幅。
        max (int): キャリブレーション後の最大位置のパルス幅。
    """
    DEF_CONF_FILE = './servo.json'

    ANGLE_MIN = -90.0
    ANGLE_MAX = 90.0
    ANGLE_CENTER = 0.0

    def __init__(self, pi, pin,
                 conf_file=DEF_CONF_FILE,
                 debug=False):
        """CalibrableServoオブジェクトを初期化する。

        親クラスのPiServoを初期化した後、設定ファイルを読み込み、
        キャリブレーション値を適用する。
        設定ファイルが存在しない場合は、デフォルト値で作成される。

        Args:
            pi (pigpio.pi): pigpio.piのインスタンス。
            pin (int): サーボが接続されているGPIOピン番号。
            conf_file (str, optional): キャリブレーション設定ファイル。
                                       デフォルトは'./servo.json'。
            debug (bool, optional): デバッグログを有効にするフラグ。
                                    デフォルトはFalse。
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug(f'pin={pin}')
        self._log.debug(f'conf_file={conf_file}')

        super().__init__(pi, pin, debug)

        self.conf_file = conf_file

        self.center = super().CENTER
        self.min = super().MIN
        self.max = super().MAX
        self._log.debug(
            f'center,min,max={self.center},{self.min},{self.max}'
        )

        res = self.load_conf()
        self._log.debug(f'res={res}')

        self.save_conf()

    def _normalize_pulse(self, pulse):
        """パルス幅を正規化する。

        指定されたパルス幅が `None` の場合は現在のパルス幅を使用し、
        `PiServo.MIN` と `PiServo.MAX` の範囲に収まるように調整する。

        Args:
            pulse (int | None): 正規化するパルス幅。Noneの場合は現在の値を取得する。

        Returns:
            int: 正規化されたパルス幅。
        """
        self._log.debug(f'pulse={pulse}')

        # `pulse`が指定されなければ、現在のパルス値を使う
        if pulse is None:
            pulse = self.get_pulse()

        # 範囲をチェックして、パルスの範囲を修正
        #   範囲: super().MIN <= pulse <= super().MAX
        if pulse < super().MIN:
            self._log.warning(f'pulse({pulse}) < {super().MIN}')
            pulse = super().MIN

        if pulse > super().MAX:
            self._log.warning(f'pulse({pulse}) > {super().MAX}')
            pulse = super().MAX

        self._log.debug(f'pulse={pulse}')
        return pulse

    def set_center(self, pulse=None):
        """中央位置のパルス幅を設定し、設定ファイルに保存する。

        Args:
            pulse (int): 新しい中央位置のパルス幅。

        Returns:
            int: 設定された中央位置のパルス幅。
        """

        pulse = self._normalize_pulse(pulse)
        self._log.debug(f'pulse={pulse}')

        self.center = pulse

        self.save_conf()

        return self.center

    def set_min(self, pulse=None):
        """最小位置のパルス幅を設定し、設定ファイルに保存する。

        Args:
            pulse (int): 新しい最小位置のパルス幅。

        Returns:
            int: 設定された最小位置のパルス幅。
        """

        pulse = self._normalize_pulse(pulse)
        self._log.debug(f'pulse={pulse}')

        self.min = pulse

        self.save_conf()

        return self.min

    def set_max(self, pulse=None):
        """最大位置のパルス幅を設定し、設定ファイルに保存する。

        Args:
            pulse (int): 新し��最大位置のパルス幅。

        Returns:
            int: 設定された最大位置のパルス幅。
        """

        pulse = self._normalize_pulse(pulse)
        self._log.debug(f'pulse={pulse}')

        self.max = pulse

        self.save_conf()

        return self.max

    def move(self, pulse):
        """サーボモーターを、キャリブレーション値を考慮して移動させる。

        指定されたパルス幅がキャリブレーションされた最小値(`self.min`)と
        最大値(`self.max`)の範囲外の場合、モーターは動かない。

        Args:
            pulse (int): 設定するパルス幅 (マイクロ秒)。
        """
        self._log.debug(f'pin={self.pin},pulse={pulse}')

        if pulse < self.min:
            self._log.warning(f'pulse({pulse}) < self.min({self.min})')
            return

        if pulse > self.max:
            self._log.warning(f'pulse({pulse}) > self.max({self.max})')
            return
            pulse = self.max

        self._log.debug(f'pulse={pulse}')
        super().move(pulse)

    def move_center(self):
        """サーボモーターをキャリブレーションされた中央位置に移動させる。
        """
        self._log.debug(f'pin={self.pin}')
        
        self.move(self.center)
        
    def move_min(self):
        """サーボモーターをキャリブレーションされた最小位置に移動させる。
        """
        self._log.debug(f'pin={self.pin}')
        
        self.move(self.min)
        
    def move_max(self):
        """サーボモーターをキャリブレーションされた最大位置に移動させる。
        """
        self._log.debug(f'pin={self.pin}')
        
        self.move(self.max)

    def deg2pulse(self, deg:float) -> int:
        """角度をパルス幅に変換する。

        キャリブレーションされた中央、最小、最大のパルス幅に基づいて、
        指定された角度(-90.0から90.0度)を対応するパルス幅に変��する。

        Args:
            deg (float): 変換する角度。

        Returns:
            int: 変換されたパルス幅。
        """
        if deg >= self.ANGLE_CENTER:
            d = self.max - self.center
        else:
            d = self.center - self.min

        pulse_float = d / self.ANGLE_MAX * deg + self.center
        pulse_int = int(round(pulse_float))

        self._log.debug(
            f'deg={deg},d={d},' +
            f'pulse_float={pulse_float},' +
            f'pulse_int={pulse_int}'
        )

        return pulse_int

    def move_angle(self, deg: float):
        """指定された角度にサーボモーターを移動させる。

        角度は-90.0から90.0度の範囲で指定する。
        範囲外の値が指定された場合は警告ログが出力される。

        Args:
            deg (float): 目標の角度。
        """
        self._log.debug(f'pin={self.pin}, deg={deg}')

        if deg < self.ANGLE_MIN:
            self._log.warning(f'deg({deg}) < ANGLE_MIN({self.ANGLE_MIN})')

        if deg > self.ANGLE_MAX:
            self._log.warning(f'deg({deg}) < ANGLE_MAX({self.ANGLE_MAX})')

        pulse = self.deg2pulse(deg)
        self._log.debug(f'pulse={pulse}')

        self.move(pulse)
        
    def read_jsonfile(self, conf_file=None):
        """設定ファイルを読み込み、内容を返す。

        ファイルが存在しない、または読み込みに失敗した場合は、
        空のリストを返す。

        Args:
            conf_file (str, optional): 読み込む設定ファイルへのパス。
                                       Noneの場合、インスタンスのデフォルトパスを使用。
                                       デフォルトはNone。

        Returns:
            list: 読み込んだ設定データ���リスト。
        """
        self._log.debug(f'conf_file={conf_file}')
        if conf_file is None:
            conf_file = self.conf_file
        self._log.debug(f'conf_file={conf_file}')

        data = []
        try:
            with open(conf_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._log.debug(f'data={data}')
                
        except Exception as e:
            self._log.error(f'{type(e).__name__}: {e}')

        return data

    def load_conf(self, conf_file=None):
        """設定ファイルからこのサーボのキャリブレーション値を読み込む。

        Args:
            conf_file (str, optional): 読み込む設定ファイルへのパス。
                                       Noneの場合、インスタンスのデフォルトパスを使用。
                                       デフォルトはNone。

        Returns:
            tuple[int, int, int]: 読み込んだ (center, min, max) のタプル。
        """
        self._log.debug(f'conf_file={conf_file}')
        if conf_file is None:
            conf_file = self.conf_file
        self._log.debug(f'conf_file={conf_file}')

        # set default
        self.center, self.min, self.max = (
            super().CENTER, super().MIN, super().MAX
        )
        center, min, max = None, None, None

        data = self.read_jsonfile(conf_file)
        self._log.debug(f'data={data}')

        for pindata in data:
            if pindata['pin'] == self.pin:
                try:
                    center = pindata['center']
                except Exception as e:
                    self._log.warning(f'{type(e).__name__}: {e}')

                try:
                    min = pindata['min']
                except Exception as e:
                    self._log.warning(f'{type(e).__name__}: {e}')

                try:
                    max = pindata['max']
                except Exception as e:
                    self._log.warning(f'{type(e).__name__}: {e}')

                break

        self._log.debug(f'center,min,max={center},{min},{max}')

        if center is not None:
            self.center = center
        if min is not None:
            self.min = min
        if max is not None:
            self.max = max

        self._log.debug(f'self.center,self.min,self.max={self.center},{self.min},{self.max}')
        return self.center, self.min, self.max

    def save_conf(self, conf_file=None):
        """現在のキャリブレーション値を設定ファイルに保存する。

        既存の設定ファイルから一度すべてのピンのデータを読み込み、
        このインスタンスのピンのデータのみを更新（または新規追加）してから、
        ピン番号でソートして書き戻す。

        Args:
            conf_file (str, optional): 保存する設定ファイルへのパス。
                                       Noneの場合、インスタンスのデフォルトパスを使用。
                                       デフォルトはNone。
        """
        self._log.debug(f'conf_file={conf_file}')
        if conf_file is None:
            conf_file = self.conf_file
        self._log.debug(f'conf_file={conf_file}')

        # read JSON data
        data = self.read_jsonfile(conf_file)
        self._log.debug(f'data={data}')

        # delete my element
        data = [pindata for pindata in data if pindata['pin'] != self.pin]
        self._log.debug(f'data={data}')

        # append my element
        data.append({
            'pin': self.pin,
            'min': self.min,
            'center': self.center,
            'max': self.max
        })
        self._log.debug(f'data={data}')

        # sort data
        data = sorted(data, key=lambda d: d['pin'])
        self._log.debug(f'data={data}')

        # write data
        try:
            with open(conf_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self._log.error(f'{type(e).__name__}: {e}')
