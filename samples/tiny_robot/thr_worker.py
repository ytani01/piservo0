#
# (c) 2025 Yoichi Tanibayashi
#
import time
import threading
import queue

from piservo0 import get_logger
from .util import Util


class ThrWorker(threading.Thread):
    """ Thread worker """

    DEF_RECV_TIMEOUT = 0.2  # sec

    def __init__(self, mservo, move_sec, angle_unit, interval_sec,
                 debug=False
    ):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('mservo.pins=%s', mservo.pins)
        self._log.debug('move_sec=%s,angle_unit=%s,interval_sec=%s',
                        move_sec, angle_unit, interval_sec)

        self.mservo = mservo
        self.move_sec = move_sec
        self.angle_unit = angle_unit
        self.interval_sec = interval_sec

        self._cmdq = queue.Queue()
        self._active = False

        self.util = Util(
            self.mservo, self.move_sec, self.angle_unit,
            debug=self._dbg
        )

        super().__init__(daemon=True)

    def __del__(self):
        """ del """

        self._active = False
        self._log.debug('')

    def end(self):
        """ end """
        self._log.debug('')
        self._active = False
        self.join()

        self._log.debug('done')

    def send(self, cmd):
        """ send """
        self._log.debug('cmd=%a', cmd)
        self._cmdq.put(cmd)

    def recv(self, timeout=DEF_RECV_TIMEOUT):
        """ recv """

        try:
            cmd = self._cmdq.get(timeout=timeout)
        except queue.Empty:
            cmd = ''
        else:
            self._log.debug('cmd=%a', cmd)

        return cmd

    def run(self):
        """ run """

        self._active = True
        while self._active:
            _cmdline = self.recv()

            if _cmdline == '':
                time.sleep(0.1)
                continue

            self._log.debug('_cmdline=%a', _cmdline)

            _cmds = _cmdline.split()

            for _cmd in _cmds:
                _res = self.util.parse_cmd(_cmd)

                if _res["cmd"] == "angles":
                    _angles = _res["angles"]
                    self.mservo.move_angle_sync(_angles, self.move_sec)

                    self._log.debug('sleep %s sec', self.interval_sec)
                    time.sleep(self.interval_sec)

                if _res["cmd"] == "interval":
                    _sec = float(_res["sec"])

                    self._log.debug('sleep %s sec', _sec)
                    time.sleep(_sec)

                if _res["cmd"] == "error":
                    print()
                    self._log.error('%s: %s',_cmd, _res["err"])
                    print("> ", end="", flush=True)

        self._log.debug('done')
