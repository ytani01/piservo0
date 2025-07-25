#
# (c) 2025 Yoichi Tanibayashi
#
import json
from typing import Optional

from .calibrable_servo import CalibrableServo
from .multi_servo import MultiServo
from .my_logger import get_logger
from .thread_worker import ThreadWorker


class ThreadMultiServo:
    """
    サーボモーター群を非同期で制御するためのインターフェースクラス。

    内部にMultiServo（同期的な制御を担当）とThreadWorker（非同期処理を担当）
    のインスタンスを保持し、両者を協調させて動作します。

    このクラスのメソッドはすべて非同期であり、呼び出し元をブロックしません。
    すべてのコマンドはキューを通じてワーカースレッドで順次実行されます。
    """

    def __init__(
        self,
        pi,
        pins: list[int],
        first_move: bool = True,
        conf_file: str = CalibrableServo.DEF_CONF_FILE,
        debug: bool = False,
    ):
        """
        ThreadMultiServoのインスタンスを初期化します。

        Args:
            pi: pigpio.piのインスタンス。
            pins (list[int]): サーボを接続したGPIOピンのリスト。
            first_move (bool, optional):
                Trueの場合、初期化時にサーボを0度の位置に移動させます。
                デフォルトはTrue。
            conf_file (str, optional):
                キャリブレーション設定ファイルのパス。
                デフォルトはCalibrableServo.DEF_CONF_FILE。
            debug (bool, optional):
                デバッグモードを有効にするかどうかのフラグ。デフォルトはFalse。
        """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug(
            "pins=%s, first_move=%s, conf_file=%s",
            pins, first_move, conf_file
        )

        # 同期的な処理を担当するMultiServoを内包する
        self._mservo = MultiServo(pi, pins, first_move, conf_file, debug=False)
        self.servo_n = len(pins)
        self.servo = self._mservo.servo  # list of CalibrableServo

        # 非同期処理を担当するThreadWorkerを起動し、mservoを渡す
        self._worker = ThreadWorker(mservo=self._mservo, debug=self._debug)
        self._worker.start()

    @property
    def pins(self) -> list[int]:
        """サーボが接続されているGPIOピンのリスト。"""
        return self._mservo.pins

    @property
    def conf_file(self) -> str:
        """使用している設定ファイルのパス。"""
        return self._mservo.conf_file

    def end(self):
        """
        終了処理。ワーカースレッドを安全に停止させ、すべてのサーボをオフにします。
        このメソッドは同期的であり、スレッドの終了を待ってからリターンします。
        """
        self.__log.debug("Ending worker...")
        if self._worker and self._worker.is_alive():
            self._worker.end()
            self._worker.join()
        self._mservo.off()
        self.__log.debug("Worker ended.")

    def _send_cmd(self, cmd: dict):
        self._worker.send(cmd)

        """コマンドをJSON形式でThreadWorkerに送信する。(プライベートメソッド)"""
        # self._worker.send(json.dumps(cmd))

    # --- 非同期制御メソッド ---

    def move_angle(self, target_angles: list[Optional[float]]):
        """
        指定された角度に即座に移動するコマンドを非同期で送信します。

        Args:
            target_angles (list[Optional[float]]): 各サーボの目標角度のリスト。
        """
        cmd = {"cmd": "move_angle", "target_angles": target_angles}
        self._send_cmd(cmd)

    def move_angle_sync(
        self,
        target_angles: list[Optional[float]],
        move_sec: Optional[float] = None,
        step_n: Optional[int] = None,
    ):
        """
        目標角度まで滑らかに移動するコマンドを非同期で送信します。

        Args:
            target_angles (list[Optional[float]]): 各サーボの目標角度のリスト。
            move_sec (Optional[float], optional):
                移動時間(秒)。Noneの場合は現在の設定値が使われます。
            step_n (Optional[int], optional):
                分割ステップ数。Noneの場合は現在の設定値が使われます。
        """
        self.__log.debug("target_angle=%s, move_sec=%s, step_n=%s",
                         target_angles, move_sec, step_n)

        cmd = {
            "cmd": "move_angle_sync",
            "target_angles": target_angles,
            "move_sec": move_sec,
            "step_n": step_n,
        }
        self._send_cmd(cmd)

    def set_move_sec(self, sec: float):
        """
        移動時間を設定するコマンドを非同期で送信します。

        Args:
            sec (float): 移動時間(秒)。
        """
        cmd = {"cmd": "move_sec", "sec": sec}
        self._send_cmd(cmd)

    def set_step_n(self, n: int):
        """
        ステップ数を設定するコマンドを非同期で送信します。

        Args:
            n (int): ステップ数。
        """
        cmd = {"cmd": "step_n", "n": n}
        self._send_cmd(cmd)

    def set_interval(self, sec: float):
        """
        コマンド実行後のインターバルを設定するコマンドを非同期で送信します。

        Args:
            sec (float): インターバル時間(秒)。
        """
        cmd = {"cmd": "interval", "sec": sec}
        self._send_cmd(cmd)

    def sleep(self, sec: float):
        """
        指定時間スリープするコマンドを非同期で送信します。

        Args:
            sec (float): スリープ時間(秒)。
        """
        cmd = {"cmd": "sleep", "sec": sec}
        self._send_cmd(cmd)

    def off(self):
        """
        ワーカースレッドを終了し、すべてのサーボをオフにします。
        この処理は同期的です。`end()` と同じです。
        """
        self.end()

    # --- 状態取得メソッド ---

    def get_pulse(self) -> list[int]:
        """
        すべてのサーボの現在のパルス幅を取得します。
        この値はワーカースレッドの処理状態を反映した最新の値です。
        """
        return self._mservo.get_pulse()

    def get_angle(self) -> list[float]:
        """
        すべてのサーボの現在の角度を取得します。
        この値はワーカースレッドの処理状態を反映した最新の値です。
        """
        return self._mservo.get_angle()
