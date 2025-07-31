#
# (c) 2025 Yoichi Tanibayashi
#
import sys

import pigpio

from piservo0 import MultiServo, StrControl, ThreadMultiServo, get_logger


class TinyRobotApp:
    """Base App for Tiny Robot"""

    def __init__(
        self, pins, conf_file, angle_unit, move_sec, step_n,
        thread_flag=False,
        debug=False
    ):
        """constractor"""
        self._debug = debug
        self.__log = get_logger(__class__.__name__, self._debug)
        self.__log.debug("pins=%s, conf_file=%s", pins, conf_file)
        self.__log.debug(
            "angele_unit=%s, move_sec=%s, step_n=%s, thread_flag=%s",
            angle_unit, move_sec, step_n, thread_flag
        )

        self.pins = pins
        self.conf_file = conf_file
        self.angle_unit = angle_unit
        self.move_sec = move_sec
        self.step_n = step_n
        self.thread_flag = thread_flag

        self.pi = None
        self.mservo = None
        self.str_ctrl = None

    def init(self):
        """initialize"""
        self.__log.debug("")
        self.pi = pigpio.pi()
        if not self.pi.connected:
            self.__log.error("pigpio daemon is not running.")
            raise RuntimeError("pigpio daemon is not running.")

        if self.thread_flag:
            self.mservo = ThreadMultiServo(
                self.pi, self.pins, conf_file=self.conf_file,
                debug=self._debug
            )
        else:
            self.mservo = MultiServo(
                self.pi, self.pins, conf_file=self.conf_file,
                debug=self._debug
            )

        self.str_ctrl = StrControl(
            self.mservo,
            angle_unit=self.angle_unit,
            move_sec=self.move_sec,
            step_n=self.step_n,
            angle_factor=[-1, -1, 1, 1],
            debug=self._debug,
        )

    def main(self):
        """main loop
        (override this method)
        """
        self.__log.debug("")
        raise NotImplementedError()

    def end(self):
        """post-process"""
        self.__log.debug("")
        if self.mservo:
            self.mservo.off()
        if self.pi:
            self.pi.stop()
        print("\n Bye")

    def start(self):
        """start application"""
        self.__log.debug("")
        try:
            self.init()
            self.main()
        except Exception as e:
            self.__log.error("%s: %s", type(e).__name__, e, exc_info=True)
            print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        finally:
            self.end()
