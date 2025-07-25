#
# (c) 2025 Yoichi Tanibayashi
#
import json

from .calibrable_servo import CalibrableServo
from .multi_servo import MultiServo
from .my_logger import get_logger
from .thread_worker import ThreadWorker


class ThreadMultiServo(MultiServo):
    """
    MultiServoの機能を持ち、ThreadWorkerを使って非同期にサーボを制御するクラス。

    同期的なメソッド(move_angle, move_angle_sync)はMultiServoから継承。
    非同期的なメソッド(xxx_async)は、内部のThreadWorkerに処理を依頼する。
    """

    def __init__(
        self,
        pi,
        pins: list[int],
        first_move=True,
        conf_file=None,
        debug=False,
    ):
        """
        コンストラクタ
        """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("pins=%s, conf_file=%s", pins, conf_file)

        # conf_fileがNoneの場合、デフォルト値を使用する
        if conf_file is None:
            conf_file = CalibrableServo.DEF_CONF_FILE

        # 親クラス(MultiServo)の初期化
        super().__init__(pi, pins, first_move, conf_file, debug)

        # ThreadWorkerを内部に保持し、処理を移譲する
        self._worker = ThreadWorker(mservo=self, debug=self._debug)
        self._worker.start()

    def end(self):
        """
        終了処理。ThreadWorkerを安全に停止させ、サーボをオフにする。
        """
        self.__log.debug("Ending worker...")
        if self._worker and self._worker.is_alive():
            self._worker.end()
        super().off()  # 親のメソッドで全サーボをオフ
        self.__log.debug("Worker ended.")

    # --- 非同期メソッド群 ---

    def move_angle_async(self, angles, move_sec=0.0):
        """
        指定された角度に即座に移動する（非同期）。
        move_angle_sync(step_n=1) を非同期で実行することで実現する。
        """
        self.move_angle_sync_async(
            angles, move_sec=move_sec, step_n=1
        )

    def move_angle_sync_async(
        self, target_angles, move_sec=None, step_n=None
    ):
        """
        同期的に角度指定で動かす（非同期）。
        関連するパラメータと角度コマンドをThreadWorkerに送信する。
        """
        # ThreadWorker側のパラメータを更新
        if move_sec is not None:
            self.set_move_sec_async(move_sec)
        if step_n is not None:
            self.set_step_n_async(step_n)

        # 角度を動かす本体のコマンドを送信
        cmd = {"cmd": "angles", "angles": target_angles}
        self._worker.send(json.dumps(cmd))

    def set_move_sec_async(self, sec: float):
        """
        移動時間を設定する（非同期）。
        """
        cmd = {"cmd": "move_sec", "sec": sec}
        self._worker.send(json.dumps(cmd))

    def set_step_n_async(self, n: int):
        """
        ステップ数を設定する（非同期）。
        """
        cmd = {"cmd": "step_n", "n": n}
        self._worker.send(json.dumps(cmd))

    def set_interval_async(self, sec: float):
        """
        インターバルを設定する（非同期）。
        """
        cmd = {"cmd": "interval", "sec": sec}
        self._worker.send(json.dumps(cmd))

    def sleep_async(self, sec: float):
        """
        指定時間スリープする（非同期）。
        """
        cmd = {"cmd": "sleep", "sec": sec}
        self._worker.send(json.dumps(cmd))

    def off_async(self):
        """
        サーボをオフにする（非同期）。
        実質的にはend()を呼び出す。
        """
        self.end()
