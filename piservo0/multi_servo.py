#
# (c) 2025 Yoichi Tanibayashi
#
from .my_logger import get_logger
from .calibrable_servo import CalibrableServo

class MultiServo:
    """
    """

    def __init__(self, pi, pins,
                 conf_file=CalibrableServo.DEF_CONF_FILE,
                 debug=False):
        """
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug(f'pins={pins}, conf_file={conf_file}')

        self.pi = pi
        self.pins = pins
        self.conf_file = conf_file

        self.servo = []
        for pin in pins:
            self.servo.append(CalibrableServo(pi, pin,
                                              conf_file=self.conf_file,
                                              debug=self._dbg))

    def move_angle(self, angle):
        """
        """
        self._log.debug(f'angle={angle}')

        if len(angle) != len(self.servo):
            self._log.error(f'len(angle)={len(angle)} != {len(self.servo)}')
            return

        for i, s in enumerate(self.servo):
            self._log.debug(f'pin={s.pin},angle={angle[i]}')
            self.servo[i].move_angle(angle[i])

    def get_pulse(self):
        pulse = []

        for s in self.servo:
            pulse.append(s.get_pulse())

        self._log.debug(f'pulse={pulse}')
        return pulse

    def move_angle_sync(self, angle, step_n=10, step_sec=0.05):
        """
        """
        # paraeters check
        if len(angle) != len(self.servo):
            self._log.error(f'len(angle)={len(angle)} != {len(self.servo)}')
            return

        # 移動前の角度のリストと、目的角度との差(絶対値)のリストを求める
        src_angle = d_angle = []
        for i, s in enumerate(self.servo):
            src_angle1 = s.get_angle()
            d_angle1 = abs(angle[i] - src_angle1)

            src_angle.append(src_angle1)
            d_angle.append(d_angle1)

        self._log.debug(f'src_angle={src_angle},d_angle={d_angle}')
