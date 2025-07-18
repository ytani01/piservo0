#
# (c) 2025 Yoichi Tanibayashi
#
import time
import pigpio
from .piservo import PiServo
from .my_logger import get_logger


class CmdServo:
    """ servo command """
    def __init__(self, pi, pin, pulse, sec=1.0, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pin=%s, pulse="%s", sec=%s', pin, pulse, sec)

        self.pin = pin
        self.pulse_str = pulse
        self.sec = sec

        self.pi = pi
        if not self.pi.connected:
            self._log.error('pigpio daemon not connected.')
            raise ConnectionError('pigpio daemon not connected.')

        self.servo = PiServo(self.pi, self.pin, debug=self._dbg)

    def main(self):
        """ main """
        self._log.debug('')

        try:
            pulse_int = int(self.pulse_str)
        except ValueError:
            if self.pulse_str == "min":
                pulse_int = PiServo.MIN
            elif self.pulse_str == "max":
                pulse_int = PiServo.MAX
            elif self.pulse_str == "center":
                pulse_int = PiServo.CENTER
            else:
                self._log.warning('"%s": invalid pulse string', self.pulse_str)
                pulse_int = -1

            self._log.debug('pulse_int=%s', pulse_int)

        if PiServo.MIN <= pulse_int <= PiServo.MAX:
            self.servo.move_pulse(pulse_int)
            time.sleep(self.sec)
        else:
            self._log.error('pulse_int=%s: invalid value. do nothing',
                            pulse_int)

    def end(self):
        """ end """
        self._log.debug('')
        self.servo.off()
        print('bye!')
