#
# (c) 2025 Yoichi Tanibayashi
#
import json
import threading
import time
import queue

from .my_logger import get_logger


class ThrWorker(threading.Thread):
    """ Thred worker """

    DEF_RECV_TIMEOUT = 0.2  # sec
    DEF_INTERVAL_SEC = 0.0  # sec

    def __init__(self, mservo, debug=False):
        """ constructor """
        self._debug = debug
        self._log = get_logger(__class__.__name__, self._debug)
        self._log.debug("")

        self.mservo = mservo
        self.move_sec = mservo.DEF_ESTIMATED_TIME
        self.step_n = mservo.DEF_STEP_N

        self.interval_sec = self.DEF_INTERVAL_SEC

        self._cmdq = queue.Queue()
        self._active = False

        super().__init__(daemon=True)

    def __del__(self):
        """ del """
        self._active = False
        self._log.info("")

    def end(self):
        """ end worker """
        self._log.debug("")
        self._active = False
        self.cmdq_clear()
        self.join()
        self._log.debug("done")

    def cmdq_clear(self):
        """ clear command queue """
        _count = 0
        while not self._cmdq.empty():
            _count += 1
            _cmd = self._cmdq.get()
            self._log.info("%2d:%s", _count, _cmd)

    def send(self, cmd):
        """ send """
        self._log.debug("cmd=%s", cmd)
        self._cmdq.put(cmd)

    def recv(self, timeout=DEF_RECV_TIMEOUT):
        """ recv """
        try:
            _cmd = self._cmdq.get(timeout=timeout)
        except queue.Empty:
            _cmd = ""
        else:
            self._log.debug("_cmd=%a", _cmd)

        return _cmd

    def run(self):
        """ run """
        self._log.debug("")

        self._active = True

        while self._active:
            _cmd = self.recv()

            if _cmd == "":
                time.sleep(0.1)
                continue

            self._log.debug("_cmd=%a", _cmd)

            try:
                # 文字列の場合は、JSONと仮定して変換
                if isinstance(_cmd, str):
                    _cmd = json.loads(_cmd)
                    self._log.debug("json.loads() --> _cmd=%a", _cmd)

                # e.g. {"cmd": "angles", "angles": [30, 0, -30, 0]}
                if _cmd["cmd"] == "angles":
                    _angles = _cmd["angles"]

                    self._log.debug("move: %s", _angles)
                    self.mservo.move_angle_sync(
                        _angles, self.move_sec, self.step_n
                    )
                    if self.interval_sec > 0:
                        self._log.debug(
                            "sleep interval_sec: %s sec",
                            self.interval_sec
                        )
                        time.sleep(self.interval_sec)
                    continue

                # e.g. {"cmd": "move_sec", "sec": 1.5}
                if _cmd["cmd"] == "move_sec":
                    self.move_sec = float(_cmd["sec"])
                    self._log.debug("move_sec=%s", self.move_sec)
                    continue

                # e.g. {"cmd": "step_n", "n": 40}
                if _cmd["cmd"] == "step_n":
                    self.step_n = int(_cmd["n"])
                    self._log.debug("step_n=%s", self.step_n)
                    continue

                # e.g. {"cmd": "interval", "sec": 0.5}
                if _cmd["cmd"] == "interval":
                    self.interval_sec = float(_cmd["sec"])
                    self._log.debug(
                        "set interval_sec=%s", self.interval_sec
                    )
                    continue

                # e.g. {"cmd": "sleep", "sec": 1.0}
                if _cmd["cmd"] == "sleep":
                    _sec = float(_cmd["sec"])
                    self._log.debug("sleep: %s sec", _sec)
                    time.sleep(_sec)
                    continue

                self._log.error("ERROR: %s", _cmd)

            except Exception as _e:
                self._log.error("%s: %s", type(_e).__name__, _e)

        self._log.debug("done")
