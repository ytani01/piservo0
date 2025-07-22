#
# (c) 2025 Yoichi Tanibayashi
#
import threading
import queue

form piservo0 import get_logger


class ThrWorker(threading.Thread):
    """ Thread worker """

    DEF_RECV_TIMEOUT = 0.2  # sec

    def __init__(self, debug=False):
        self._debug = debug
        self._log = get_logger(__class__.__name__, self._debug)
        self._log.debug('')

        self._cmdq = queue.Queue()
        self._active = False

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
            _cmd = self.recv()

            if _cmd == '':
                time.sleep(0.1)
                continue

            self._log.debug('cmd=%a', cmd)

        self._log.debug('done')
