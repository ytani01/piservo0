import pigpio
from .my_logger import get_logger

DEF_PIN = 18

class PiServo:
    OFF = 0
    MIN = 500
    MAX = 2500
    CENTER = 1500

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

        if pulse < self.MIN:
            self._log.warn(f'{pulse} < MIN({self.MIN})')
            pulse = self.MIN

        if pulse > self.MAX:
            self._log.warn(f'{pulse} > MAX({self.MAX})')
            pulse = self.MAX

        self.pi.set_servo_pulsewidth(self.pin, pulse)
    
    def off(self):
        self._log.debug('pin={self.pin}')

        self.pi.set_servo_pulsewidth(self.pin, self.OFF)
