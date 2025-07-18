#
# (c) 2025 Yoichi Tanibayashi
#
import sys
import random
import pigpio
from piservo0 import get_logger
from piservo0 import MultiServo


class App:
    """  """

    SLEEP_SEC = 0.5

    # [-FL, -BL, BR, FR]
    CMD1 = [
        [-45, 0, 0, 0],
        [-45, 45, -45, -45],
        [0, 0, -45, -45],
        [0, -45, -45, -45],
        [45, -45, -45, 45],
        [45, 0, 0, 0],
        [0, 0, 0, 0],
    ]

    CMD2 = [
        [0, 0, 0, 45],
        [45, 45, -45, 45],
        [45, 45, 0, 0],
        [45, 45, 45, 0],
        [-45, 45, 45, -45],
        [0, 0, 0, -45],
        [0, 0, 0, 0],
    ]

    def __init__(self, pi, pins, conf_file='./servo.json', debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pins=%s, conf_file=%s', pins, conf_file)

        self.pi = pi
        self.pins = pins
        self.conf_file = conf_file

        self.mservo = MultiServo(self.pi, self.pins,
                                 conf_file=self.conf_file,
                                 debug=self._dbg)

    def main(self):
        """  """
        self._log.debug('')

        for i in range(3):
            for p in self.CMD1 + self.CMD2:
                self.mservo.move_angle_sync(p, self.SLEEP_SEC)

    def end(self):
        """  """
        self._log.debug("")
        self.mservo.off()


if __name__ == '__main__':
    pins = [17, 27, 22, 23]

    # init
    try:
        pi = pigpio.pi()
        app = App(pi, pins, debug=False)

    except Exception as _e:
        print('%s: %s' % (type(_e).__name__, _e))
        sys.exit()

    try:
        app.main()

    except Exception as _e:
        print('%s: %s' % (type(_e).__name__, _e))

    finally:
        pi.stop()
        print('\n Bye')
