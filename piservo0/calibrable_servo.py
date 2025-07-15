#
# (c) 2025 Yoichi Tanibayashi
#
from .my_logger import get_logger
from .piservo import PiServo
from .servo_config_manager import ServoConfigManager

class CalibrableServo(PiServo):
    """PiServoを拡張し、キャリブレーション機能を追加したクラス。

    サーボモーターの制御に特化し、設定の永続化はServoConfigManagerに委任する。

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

        親クラスを初期化した後、ServoConfigManagerを使って設定を読み込む。
        設定が存在しない場合は、デフ��ルト値で作成する。

        Args:
            pi (pigpio.pi): pigpio.piのインスタンス。
            pin (int): サーボが接続されているGPIOピン番号。
            conf_file (str, optional): キャリブレーション設定ファイル。
            debug (bool, optional): デバッグログを有効にするフラグ。
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug(f'pin={pin}, conf_file={conf_file}')

        super().__init__(pi, pin, debug)

        self._config_manager = ServoConfigManager(conf_file, self._dbg)

        # デフォルト値を設定
        self.min = super().MIN
        self.center = super().CENTER
        self.max = super().MAX

        # 設定を読み込んで適用
        self.load_conf()
        
        # 設定ファイルにこのピンの情報がなければ、現在のデフォルト値で保存する
        self._ensure_config_exists()

    def _normalize_pulse(self, pulse):
        """パルス幅を正規化する。(プライベートメソッド)

        指定されたパルス幅が `None` の場合は現在のパルス幅を使用し、
        `PiServo.MIN` と `PiServo.MAX` の範囲に収まるように調整する。

        Args:
            pulse (int | None): 正規化するパルス幅。

        Returns:
            int: 正規化されたパルス幅。
        """
        if pulse is None:
            pulse = self.get_pulse()

        if pulse < super().MIN:
            self._log.warning(f'pulse({pulse}) < {super().MIN}')
            pulse = super().MIN

        if pulse > super().MAX:
            self._log.warning(f'pulse({pulse}) > {super().MAX}')
            pulse = super().MAX

        return pulse

    def set_center(self, pulse=None):
        """中央位置のパルス幅を設定し、設定ファイルに保存する。"""
        self.center = self._normalize_pulse(pulse)
        self.save_conf()
        return self.center

    def set_min(self, pulse=None):
        """最小位置のパルス幅を設定し、設定ファイルに保存する。"""
        self.min = self._normalize_pulse(pulse)
        self.save_conf()
        return self.min

    def set_max(self, pulse=None):
        """最大位置のパルス幅を設定し、設定ファイルに保存する。"""
        self.max = self._normalize_pulse(pulse)
        self.save_conf()
        return self.max

    def move(self, pulse):
        """サーボモーターを、キャリブレーション値を考慮して移動させる。

        指���されたパルス幅がキャリブレーション範囲外の場合、モーターは動かない。
        """
        if pulse < self.min:
            self._log.warning(f'pulse({pulse}) < self.min({self.min})')
            return
        if pulse > self.max:
            self._log.warning(f'pulse({pulse}) > self.max({self.max})')
            return
        
        super().move(pulse)

    def move_center(self):
        """サーボモーターをキャリブレーションされた中央位置に移動させる。"""
        self._log.debug('')
        self.move(self.center)
        
    def move_min(self):
        """サーボモーターをキャリブレーションされた最小位置に移動させる。"""
        self._log.debug('')
        self.move(self.min)
        
    def move_max(self):
        """サーボモーターをキャリブレーションされた最大位置に移動させる。"""
        self._log.debug('')
        self.move(self.max)

    def deg2pulse(self, deg:float) -> int:
        """角度をパルス幅に変換する。"""
        if deg >= self.ANGLE_CENTER:
            d = self.max - self.center
        else:
            d = self.center - self.min

        pulse_float = d / self.ANGLE_MAX * deg + self.center
        pulse_int = int(round(pulse_float))
        self._log.debug(
            f'deg={deg},pulse_float={pulse_float},pulse_int={pulse_int}'
        )

        return pulse_int

    def move_angle(self, deg: float):
        """指定された角度にサーボモーターを移動させる。"""
        self._log.debug(f'deg={deg}')

        if deg < self.ANGLE_MIN:
            self._log.warning(f'deg({deg}) < ANGLE_MIN({self.ANGLE_MIN})')
            return
        if deg > self.ANGLE_MAX:
            self._log.warning(f'deg({deg}) > ANGLE_MAX({self.ANGLE_MAX})')
            return

        pulse = self.deg2pulse(deg)

        self.move(pulse)
        
    def load_conf(self):
        """設定ファイルからこのサーボのキャリブレーション値を読み込む。"""
        config = self._config_manager.get_config(self.pin)
        if config:
            self.min = config.get('min', self.min)
            self.center = config.get('center', self.center)
            self.max = config.get('max', self.max)
        self._log.debug(f"Loaded: pin={self.pin}, min={self.min}, center={self.center}, max={self.max}")

    def save_conf(self):
        """現在のキャリブレーション値を設定ファイルに保存する。"""
        new_config = {
            'pin': self.pin,
            'min': self.min,
            'center': self.center,
            'max': self.max
        }
        self._config_manager.save_config(new_config)
        self._log.debug(f"Saved: {new_config}")

    def _ensure_config_exists(self):
        """もし設定がなければ、現在の値で保存する。(プライベート��ソッド)"""
        if self._config_manager.get_config(self.pin) is None:
            self._log.warning(f"No config for pin {self.pin}. Saving current values.")
            self.save_conf()
