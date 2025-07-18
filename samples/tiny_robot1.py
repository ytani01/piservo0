#
# (c) 2025 Yoichi Tanibayashi
#
import sys
import time
import random
import pigpio
from piservo0 import get_logger
from piservo0 import MultiServo


class App:
    """ Tiny Robot App
    """
    #      [FL, BL, BR, FR]
    PINS = [23, 22, 27, 17]

    # 遅延時間
    SLEEP_SEC = .2

    # コマンドシーケンス
    #
    # - [Front-Left, Back-Left, Back-Right, Front-Right]
    #
    # - ここでは、プラスの角度が前方向になるように書く。
    #
    ANGLE_UNIT = 30

    F = ANGLE_UNIT  # move leg forward
    B = -ANGLE_UNIT  # move leg backward
    C = 0  # move leg center

    # (左右反転パターンは、flip_angles()で生成できる)
    SEQ = [
        #FL,BL,BR,FR
        [F, C, C, C],
        [F, B, B, B],
        [C, C, B, B],
        [C, F, B, B],
        [B, F, B, C],
        [B, C, B, F],
        [B, C, C, C],
        [C, C, C, C],
    ]

    # SEQの角度をサーボに与える実際の角度に変換するための係数
    ANGLE_DIR = [1, 1, -1, -1]

    def __init__(self, pi_, pins=PINS,
                 conf_file='./servo.json',
                 debug=False):
        """ constractor """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pins=%s, conf_file=%s', pins, conf_file)

        self.pi = pi_
        self.pins = pins
        self.conf_file = conf_file

        self.mservo = MultiServo(self.pi, self.pins,
                                 conf_file=self.conf_file,
                                 #debug=self._dbg)
                                 debug=False)

    def main(self):
        """ main function """
        self._log.debug('')

        time.sleep(1.0)
        
        for _count in range(10):
            print(f'===== count={_count}')

            for angles in self.SEQ + self.flip_angles(self.SEQ):

                # プラスの角度が前になるようになっているのを
                # 実際の角度に戻す
                self._log.debug('angles=%s', angles)
                _d = self.ANGLE_DIR
                angles2 = [angles[_i] * _d[_i] for _i in range(len(_d))]
                self._log.debug('angles2=%s', angles2)

                self.mservo.move_angle_sync(angles2, self.SLEEP_SEC)

    def end(self):
        """ end: post-processing """
        self._log.debug("")
        self.mservo.off()

    def flip_angles(self, seq):
        """ Flip the array for left/right switching

        e.g.
          from
          [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
          ]

          to
          [
            [4, 3, 2, 1],
            [8, 7, 6, 5],
          ]
        """
        for _c in seq:
            self._log.debug('  %s', _c)

        new_seq = []
        for c in seq:
            c.reverse()
            new_seq.append(c)

        for _c in new_seq:
            self._log.debug('  %s', _c)

        return new_seq
        

if __name__ == '__main__':
    # init
    try:
        pi = pigpio.pi()
        app = App(pi, debug=True)

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
