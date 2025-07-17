#
# (c) 2025 Yoichi Tanibayashi
#
import time
from .my_logger import get_logger
from .calibrable_servo import CalibrableServo


class MultiServo:
    """
    Controls multiple servo motors.
    """

    def __init__(self, pi, pins, first_move=True,
                 conf_file=CalibrableServo.DEF_CONF_FILE,
                 debug=False):
        """
        Initializes the MultiServo instance.
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug(f'pins={pins}, conf_file={conf_file}')

        self.pi = pi
        self.pins = pins
        self.servo_n = len(pins)
        self.conf_file = conf_file
        self.first_move = first_move

        self.servo = [
            CalibrableServo(pi, pin, conf_file=self.conf_file, debug=False)
            for pin in pins
        ]

        if self.first_move:
            self.move_angle([0] * self.servo_n)

    def _validate_angle_list(self, angles):
        """
        Validates the list of angles.
        Returns True if valid, False otherwise.
        """
        if not isinstance(angles, (list, tuple)):
            self._log.error(f'angles must be a list or tuple: {type(angles)}')
            return False

        if len(angles) != self.servo_n:
            self._log.error(f'len(angles)={len(angles)} != {self.servo_n}')
            return False

        return True

    def off(self):
        """
        Turns off all servos.
        """
        self._log.debug('')
        for s in self.servo:
            s.off()

    def get_pulse(self):
        """
        Gets the current pulse width of all servos.
        """
        pulses = [s.get_pulse() for s in self.servo]
        self._log.debug(f'pulses={pulses}')
        return pulses

    def move_pulse(self, pulses, forced=False):
        """   """
        for i, s in enumerate(self.servo):
            self._log.debug(f'pin=s.pin, pulse={pulses[i]}')
            s.move_pulse(pulses[i], forced)

    def get_angle(self):
        """
        Gets the current angle of all servos.
        """
        angles = [s.get_angle() for s in self.servo]
        self._log.debug(f'angles={angles}')
        return angles

    def move_angle(self, angles):
        """
        Moves each servo to the specified angle.
        """
        self._log.debug(f'angles={angles}')

        if not self._validate_angle_list(angles):
            return

        for i, s in enumerate(self.servo):
            self._log.debug(f'pin={s.pin}, angle={angles[i]}')
            s.move_angle(angles[i])

    def move_angle_sync(self, target_angles, estimated_sec=1.0, step_n=50):
        """
        Moves all servos synchronously and smoothly to target angles.
        """
        self._log.debug(
            f'target_angles={target_angles}, estimated_sec={estimated_sec}, step_n={step_n}'
        )

        if not self._validate_angle_list(target_angles):
            return

        if step_n < 1:
            self.move_angle(target_angles)
            return

        step_sec = estimated_sec / step_n
        self._log.debug(f'step_sec={step_sec}')

        start_angles = self.get_angle()
        self._log.debug(f'start_angles={start_angles}')

        diff_angles = [
            target_angles[i] - start_angles[i] for i in range(self.servo_n)
        ]
        self._log.debug(f'diff_angles={diff_angles}')

        for step_i in range(1, step_n + 1):
            next_angles = [
                start_angles[i] + diff_angles[i] * step_i / step_n
                for i in range(self.servo_n)
            ]
            self.move_angle(next_angles)
            self._log.debug(
                f'step {step_i}/{step_n}: ' +
                f'next_angles={next_angles}, ' +
                f'step_sec={step_sec}'
            )
            time.sleep(step_sec)
