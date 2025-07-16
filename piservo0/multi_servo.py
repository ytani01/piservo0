#
# (c) 2025 Yoichi Tanibayashi
#
import time
from .my_logger import get_logger
from .calibrable_servo import CalibrableServo

class MultiServo:
    """
    """

    def __init__(self, pi, pins, first_move=True,
                 conf_file=CalibrableServo.DEF_CONF_FILE,
                 debug=False):
        """
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug(f'pins={pins}, conf_file={conf_file}')

        self.pi = pi
        self.pins = pins
        self.servo_n = len(pins)
        self.conf_file = conf_file

        self.servo = []
        for pin in pins:
            self.servo.append(CalibrableServo(pi, pin,
                                              conf_file=self.conf_file,
                                              debug=False))
                                              # debug=self._dbg))

        self.move_angle([0] * self.servo_n)

    def off(self):
        """
        """
        self._log.debug('')

        for s in self.servo:
            s.off()

    def get_pulse(self):
        """
        """
        pulse = []

        for s in self.servo:
            pulse.append(s.get_pulse())

        self._log.debug(f'pulse={pulse}')
        return pulse

    def get_angle(self):
        """
        """
        angle = []

        for s in self.servo:
            angle.append(s.get_angle())

        self._log.debug(f'angle={angle}')
        return angle

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

    def move_angle_sync(self, angle, estimated_sec=1.0, step_n=50):
        """
        全てのサーボを同期させて動かす。
        """
        self._log.debug(
            f'angle={angle},estimated_sec={estimated_sec},step_n={step_n}'
        )
        
        # paraeters check
        if len(angle) != len(self.servo):
            self._log.error(f'len(angle)={len(angle)} != {len(self.servo)}')
            return

        # ステップ毎のスリープ時間
        step_sec = estimated_sec / step_n
        self._log.debug(f'step_sec={step_sec}')

        # 移動前の角度のリスト
        cur_angle = self.get_angle()
        self._log.debug(f'cur_angle={cur_angle}')

        # 目的角度との差分を元に、各サーボ毎にステップごとの移動量を求める
        d_angle = []
        step_angle = []
        for i, s in enumerate(self.servo):
            d_angle.append(angle[i] - cur_angle[i])
            step_angle.append(d_angle[i] / step_n)
        self._log.debug( f'd_angle={d_angle},step_angle={step_angle}')

        # 動かす
        for step_i in range(step_n):
            for servo_i in self.servo_n:
                cur_angle[servo_i] += step_angle[servo_i]
            self.move_angle(cur_angle)
            self._log.debug(f'cur_angle={cur_angle}')

            time.sleep(step_sec)
