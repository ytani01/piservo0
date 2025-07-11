import pigpio
from .my_logger import get_logger

DEF_PIN = 18

class PiServo:
    PULSE_OFF = 0
    PULSE_MIN = 500
    PULSE_MAX = 2500
    PULSE_CENTER = 1500

    def __init__(self, pin=DEF_PIN, pi=None, debug=False):
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug(f'pin={pin}')

        if type(pi) is pigpio.pi:
            self.pi = pi
            self.mypi = False
        else:
            self.pi = pigpio.pi()
            self.mypi = True
        self._log.debug(f'mypi={self.mypi}')

        self.pin = pin

    def move(self, pulse):
        self._log.debug(f'pin={self.pin}, pulse={pulse}')

        if pulse < self.PULSE_MIN:
            self._log.warn(f'{pulse} < PULSE_MIN({self.PULSE_MIN})')
            pulse = self.PULSE_MIN

        if pulse > self.PULSE_MAX:
            self._log.warn(f'{pulse} > PULSE_MAX({self.PULSE_MAX})')
            pulse = self.PULSE_MAX

        self.pi.set_servo_pulsewidth(self.pin, pulse)
    
    def off(self):
        self._log.debug('pin={self.pin}')

        self.pi.set_servo_pulsewidth(self.pin, self.PULSE_OFF)
