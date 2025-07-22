#
# (c) 2025 Yoichi Tanibayashi
#
import sys
import pigpio
from piservo0 import get_logger
from piservo0 import MultiServo
from .util import Util


class TinyRobotApp:
    """Base App for Tiny Robot"""

    def __init__(self, pins, conf_file, debug=False):
        """constractor"""
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug("pins=%s, conf_file=%s", pins, conf_file)

        self.pins = pins
        self.conf_file = conf_file

        self.pi = None
        self.mservo = None
        self.util = None

    def init(self):
        """initialize"""
        self._log.debug("")
        self.pi = pigpio.pi()
        if not self.pi.connected:
            self._log.error("pigpio daemon is not running.")
            raise RuntimeError("pigpio daemon is not running.")

        self.mservo = MultiServo(
            self.pi, self.pins, conf_file=self.conf_file, debug=False
        )
        self.util = Util(self.mservo, self.move_sec, self.angle_unit, debug=self._dbg)

    def main(self):
        """main loop
        (override this method)
        """
        self._log.debug("")
        raise NotImplementedError()

    def end(self):
        """post-process"""
        self._log.debug("")
        if self.mservo:
            self.mservo.off()
        if self.pi:
            self.pi.stop()
        print("\n Bye")

    def start(self):
        """start application"""
        self._log.debug("")
        try:
            self.init()
            self.main()
        except Exception as e:
            self._log.error("%s: %s", type(e).__name__, e, exc_info=True)
            print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        finally:
            self.end()
