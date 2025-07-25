#
# (c) 2025 Yoichi Tanibayashi
#
import json
import queue
import threading
import time

from .my_logger import get_logger


class ThreadWorker(threading.Thread):
    """ Thred worker """

    DEF_RECV_TIMEOUT = 0.2  # sec
    DEF_INTERVAL_SEC = 0.0  # sec

    def __init__(
        self, mservo,
        move_sec=None,
        step_n=None,
        interval_sec=DEF_INTERVAL_SEC, debug=False
    ):
        """ constructor """
        self._debug = debug
        self.__log = get_logger(__class__.__name__, self._debug)
        self.__log.debug("")

        self.mservo = mservo

        if move_sec is None:
            self.move_sec = mservo.DEF_MOVE_SEC
        else:
            self.move_sec = move_sec

        if step_n is None:
            self.step_n = mservo.DEF_STEP_N
        else:
            self.step_n = step_n

        self.interval_sec = self.DEF_INTERVAL_SEC

        self._cmdq = queue.Queue()
        self._active = False

        super().__init__(daemon=True)

    def __del__(self):
        """ del """
        self._active = False
        self.__log.debug("")

    def end(self):
        """ end worker """
        self.__log.debug("")
        self._active = False
        self.cmdq_clear()
        self.join()
        self.__log.debug("done")

    def cmdq_clear(self):
        """ clear command queue """
        _count = 0
        while not self._cmdq.empty():
            _count += 1
            _cmd = self._cmdq.get()
            self.__log.debug("%2d:%s", _count, _cmd)

    def send(self, cmd):
        """ send """
        self._cmdq.put(cmd)
        _qsize = self._cmdq.qsize()
        self.__log.debug("cmd=%s --> qsize=%s", cmd, _qsize)

    def recv(self, timeout=DEF_RECV_TIMEOUT):
        """ recv """
        try:
            _cmd = self._cmdq.get(timeout=timeout)
            _qsize = self._cmdq.qsize()
        except queue.Empty:
            _cmd = ""
        else:
            self.__log.debug("_cmd=%a --> qsize=%s", _cmd, _qsize)

        return _cmd

    def run(self):
        """ run """
        self.__log.debug("start")

        self._active = True

        while self._active:
            # コマンド受信
            _cmd = self.recv()
            if _cmd == "":
                time.sleep(0.1)
                continue
            self.__log.debug("_cmd=%a", _cmd)

            try:
                # 文字列の場合は、JSONと仮定して変換
                if isinstance(_cmd, str):
                    _cmd = json.loads(_cmd)
                    self.__log.debug("json.loads() --> _cmd=%a", _cmd)

                _cmd_type = _cmd["cmd"]

                # e.g. {
                #        "cmd": "move_angle_sync",
                #        "target_angles": [30, 0, -30, 0],
                #        "move_sec": 0.2,
                #        "step_n": 40
                #      }
                if _cmd_type == "move_angle_sync":
                    _target_angles = _cmd["target_angles"]
                    _move_sec = _cmd["move_sec"]
                    _step_n = _cmd["step_n"]

                    if _move_sec is None:
                        _move_sec = self.move_sec

                    if _step_n is None:
                        _step_n = self.step_n

                    self.mservo.move_angle_sync(
                        _target_angles, _move_sec, _step_n
                    )

                    if self.interval_sec > 0:
                        self.__log.debug(
                            "sleep interval_sec: %s sec",
                            self.interval_sec
                        )
                        time.sleep(self.interval_sec)
                    continue

                # e.g. {
                #        "cmd": "move_angle",
                #        "target_angles": [30, 0, -30, 0]
                #      }
                if _cmd_type == "move_angle":
                    _target_angles = _cmd["target_angles"]

                    self.mservo.move_angle(_target_angles)

                    if self.interval_sec > 0:
                        self.__log.debug(
                            "sleep interval_sec: %s sec",
                            self.interval_sec
                        )
                        time.sleep(self.interval_sec)
                    continue

                # e.g. {"cmd": "angles", "angles": [30, 0, -30, 0]}
                # 注: Pythonの None --> JSONでは null
                if _cmd_type == "angles":
                    _angles = _cmd["angles"]
                    self.__log.debug("move: %s", _angles)

                    self.mservo.move_angle_sync(
                        _angles, self.move_sec, self.step_n
                    )
                    if self.interval_sec > 0:
                        self.__log.debug(
                            "sleep interval_sec: %s sec",
                            self.interval_sec
                        )
                        time.sleep(self.interval_sec)
                    continue

                # e.g. {"cmd": "move_sec", "sec": 1.5}
                if _cmd_type == "move_sec":
                    self.move_sec = float(_cmd["sec"])
                    self.__log.debug("move_sec=%s", self.move_sec)
                    continue

                # e.g. {"cmd": "step_n", "n": 40}
                if _cmd_type == "step_n":
                    self.step_n = int(_cmd["n"])
                    self.__log.debug("step_n=%s", self.step_n)
                    continue

                # e.g. {"cmd": "interval", "sec": 0.5}
                if _cmd_type == "interval":
                    self.interval_sec = float(_cmd["sec"])
                    self.__log.debug(
                        "set interval_sec=%s", self.interval_sec
                    )
                    continue

                # e.g. {"cmd": "sleep", "sec": 1.0}
                if _cmd_type == "sleep":
                    _sec = float(_cmd["sec"])
                    self.__log.debug("sleep: %s sec", _sec)
                    time.sleep(_sec)
                    continue

                self.__log.error("ERROR: %s", _cmd)

            except Exception as _e:
                self.__log.error("%s: %s", type(_e).__name__, _e)

        self.__log.debug("done")
