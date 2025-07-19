#
# (c) 2025 Yoichi Tanibayashi
#
import sys
import time
import click
import pigpio
from piservo0 import get_logger
from piservo0 import MultiServo


# clickで、'-h'もヘルプオプションするために
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS,
             help="Tiny Robot")
@click.option('-debug', '-d', is_flag=True, help="debug flag")
@click.pass_context
def cli(ctx, debug):
    """ CLI top """
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@cli.command(help="""
Tiny Robot Demo #1

`PINS` order:\n
    PIN1 Front-Left\n
    PIN2 Back-Left\n
    PIN3 Back-Right\n
    PIN4 Front-Rihgt
""")
@click.argument('pins', type=int, nargs=4)
@click.option('--count', '-c', type=int, default=10,
              help='count')
@click.option('--move_sec', '-s', type=float, default=.2,
              help='move steop sec')
@click.option('--interval_sec', '-i', type=float, default=0.0,
              help='step interval sec')
@click.option('--conf_file', '-f', type=str, default='./servo.json',
              help='Config file path')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
def demo1(pins, count, move_sec, interval_sec, conf_file, debug):
    """ Calibrate servo motors """
    log = get_logger(__name__, debug)
    log.debug('pins=%s,count=%s,move_sec=%s,interval_sec=%s,conf_file=%s',
              pins, count, move_sec, interval_sec, conf_file)

    # init
    util = Util(debug=debug)

    try:
        pi = pigpio.pi()
        app = Demo1App(util, pi, pins, count, move_sec, interval_sec,
                       debug=debug)

    except Exception as _e:
        print('%s: %s' % (type(_e).__name__, _e))
        sys.exit()

    # main
    try:
        app.main()

    except Exception as _e:
        print('%s: %s' % (type(_e).__name__, _e))

    # end
    finally:
        #app.mservo.move_angle_sync([0, 0, 0, 0], move_sec)
        app.mservo.move_angle_sync([0, 0, 0, 0], 1)
        pi.stop()
        print('\n Bye')


class Demo1App:
    """ Tiny Robot Demo #1
    """
    # パラメータデフォルト値
    DEF_MOVE_SEC = .2
    DEF_INTERVAL_SEC = .0
    DEF_COUNT = 10

    # SEQの角度をサーボに与える実際の角度に変換するための係数
    #           [FL, BL, BR, FR]
    ANGLE_DIR = [-1, -1,  1,  1]

    # コマンドシーケンス
    #
    # - [Front-Left, Back-Left, Back-Right, Front-Right]
    # - ここでは、プラスの角度が前方向になるように書く。
    # - F:前、C:中央、B:後
    #
    ANGLE_UNIT = 45  # move angle
    F = ANGLE_UNIT  # move leg forward
    B = -ANGLE_UNIT  # move leg backward
    C = 0  # move leg center

    # (左右反転パターンは、flip_angles()で生成できる)
    SEQ = [
        #FL,BL,BR,FR
        [F, C, C, C],  # 左前足を前に出し、他は中央
        [F, B, B, B],  # 左前足は前のまま、他の3本足を後ろへ蹴る
        [C, C, B, B],
        [C, F, B, B],
        [C, F, B, C],
        [B, F, B, C],
        [B, C, B, F],
        [B, C, C, C],
        #[C, C, C, C],
    ]

    def __init__(self, util, pi_, pins,
                 count=DEF_COUNT,
                 move_sec=DEF_MOVE_SEC,
                 interval_sec=DEF_INTERVAL_SEC,
                 conf_file='./servo.json',
                 debug=False):
        """ constractor """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pins=%s,move_sec=%s,interval_sec=%s,conf_file=%s',
                        pins, move_sec, interval_sec, conf_file)

        self.util = util
        self.pi = pi_
        self.pins = pins
        self.count = count
        self.move_sec = move_sec
        self.interval_sec = interval_sec
        self.conf_file = conf_file

        self.mservo = MultiServo(self.pi, self.pins,
                                 conf_file=self.conf_file,
                                 #debug=self._dbg)
                                 debug=False)

    def main(self):
        """ main function """
        self._log.debug('')

        time.sleep(1.0)
        
        _seq = self.SEQ + self.util.flip_angles(self.SEQ)

        try:
            for _count in range(self.count):
                print(f'===== count={_count}')

                for angles_in in _seq:

                    # プラスの角度が前になるようになっているのを
                    # 実際の角度に戻す
                    _a = angles_in
                    _d = self.ANGLE_DIR
                    angles = [_a[_i] * _d[_i] for _i in range(len(_d))]
                    self._log.debug('angles=%s', angles)

                    # Move !
                    self.mservo.move_angle_sync(angles, self.move_sec)

                    time.sleep(self.interval_sec)

        except KeyboardInterrupt as _e:
            self._log.debug('\n%s', type(_e).__name__)
            #self.mservo.move_angle_sync([0, 0, 0, 0], self.move_sec)

    def end(self):
        """ end: post-processing """
        self._log.debug("")
        self.mservo.move_angle_sync([0, 0, 0, 0], .5)
        self.mservo.off()


@cli.command(help="""
Tiny Robot Manual mode

`PINS` order:\n
    PIN1 Front-Left\n
    PIN2 Back-Left\n
    PIN3 Back-Right\n
    PIN4 Front-Rihgt
""")
@click.argument('pins', type=int, nargs=4)
@click.option('--count', '-c', type=int, default=10,
              help='count')
@click.option('--move_sec', '-s', type=float, default=.2,
              help='move steop sec')
@click.option('--interval_sec', '-i', type=float, default=0.0,
              help='step interval sec')
@click.option('--conf_file', '-f', type=str, default='./servo.json',
              help='Config file path')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
def manual(pins, count, move_sec, interval_sec, conf_file, debug):
    """ Calibrate servo motors """
    log = get_logger(__name__, debug)
    log.debug('pins=%s,count=%s,move_sec=%s,interval_sec=%s,conf_file=%s',
              pins, count, move_sec, interval_sec, conf_file)

    # init
    util = Util(debug=debug)

    try:
        pi = pigpio.pi()
        app = ManualApp(util, pi, pins, count, move_sec, interval_sec,
                        debug=debug)

    except Exception as _e:
        print('%s: %s' % (type(_e).__name__, _e))
        sys.exit()

    # main
    try:
        app.main()

    except Exception as _e:
        print('%s: %s' % (type(_e).__name__, _e))

    # end
    finally:
        app.end()
        pi.stop()
        print('\n Bye')


class ManualApp:
    """ Tiny Robot Manual Mode
    """
    # パラメータデフォルト値
    DEF_MOVE_SEC = .2
    DEF_INTERVAL_SEC = .0
    DEF_COUNT = 10

    def __init__(self, util, pi_, pins,
                 count=DEF_COUNT,
                 move_sec=DEF_MOVE_SEC,
                 interval_sec=DEF_INTERVAL_SEC,
                 conf_file='./servo.json',
                 debug=False):
        """ constractor """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pins=%s,move_sec=%s,interval_sec=%s,conf_file=%s',
                        pins, move_sec, interval_sec, conf_file)

        self.util = util
        self.pi = pi_
        self.pins = pins
        self.count = count
        self.move_sec = move_sec
        self.interval_sec = interval_sec
        self.conf_file = conf_file

        self.mservo = MultiServo(self.pi, self.pins,
                                 conf_file=self.conf_file,
                                 #debug=self._dbg)
                                 debug=False)

    def main(self):
        """ main function """
        self._log.debug('')

        time.sleep(1.0)
        
        try:
            while True:
                line = input('> ')

                cmds = line.split()
                self._log.debug('cmds=%s', cmds)

                for cmd in cmds:
                    res = self.util.parse_cmd(cmd)

                    if res['cmd'] == 'angles':
                        angles = res['angles']
                        self.mservo.move_angle_sync(angles, self.move_sec)
                        time.sleep(self.interval_sec)

                    if res['cmd'] == 'interval':
                        time.sleep(float(res['sec']))

                    if res['cmd'] == 'error':
                        print(f'ERROR: {cmd}: {res["err"]}')

        except (EOFError, KeyboardInterrupt) as _e:
            self._log.debug('\n%s', type(_e).__name__)

        except Exception as _e:
            self._log.error('\n%s: %s', type(_e).__name__, _e)

    def end(self):
        """ end: post-processing """
        self._log.debug("")
        self.mservo.move_angle_sync([0, 0, 0, 0], .5)
        self.mservo.off()


class Util:
    """ utility functions """

    # SEQの角度をサーボに与える実際の角度に変換するための係数
    #                  [FL, BL, BR, FR]
    DEF_ANGLE_FACTOR = [-1, -1,  1,  1]
    
    # 一度に動かく角度の絶対値
    DEF_ANGLE_UNIT = 40

    # コマンド文字
    CH_CENTER = 'C'
    CH_FORWARD = 'F'
    CH_BACKWARD = 'B'

    def __init__(self, debug=False):
        """ constructor """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self.angle_unit=self.DEF_ANGLE_UNIT
        self.angle_factor=self.DEF_ANGLE_FACTOR

    def set_angle_unit(self, angle:float) -> float:
        """   """
        self._log.debug('angle=%s', angle)

        if angle <= 0:
            return -1

        self.angle_unit = angle

        return self.angle_unit

    def is_anglecmd(self, cmd):
        """  """
        self._log.debug('cmd=%s', cmd)

        if len(cmd) != 4:
            return False

        for _ch in cmd:
            if _ch not in (self.CH_CENTER,
                           self.CH_FORWARD,
                           self.CH_BACKWARD):
                return False

        self._log.debug('True')
        return True

    def parse_cmd(self, cmd):
        """ parse cmdline

        e.g.
          self.angle_unit = 40
          self.angle_factor = [-1, -1, 1, 1]

          'fcbf' --> ('angles', [-40,0,-40,40])

        """
        self._log.debug('cmd=%s', cmd)

        ret = None

        cmd = cmd.upper()

        if self.is_anglecmd(cmd):
            angles = []
            for _i, _ch in enumerate(cmd):
                _af = self.angle_factor[_i]

                if _ch == self.CH_CENTER:
                    angles.append(0)
                elif _ch == self.CH_FORWARD:
                    angles.append(self.angle_unit * _af)
                elif _ch == self.CH_BACKWARD:
                    angles.append(self.angle_unit * _af * -1)

            ret = {'cmd': 'angles', 'angles': angles}

        elif cmd.isnumeric():
            ret = {'cmd': 'interval', 'sec': float(cmd)}

        else:
            self._log.error('cmd="%s" invalid]', cmd)
            ret = {'cmd': 'error', 'err': 'invalid command'}

        self._log.debug('ret=%s', ret)
        return ret

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
        self._log.debug('seq =')
        for _c in seq:
            self._log.debug('  %s', _c)

        new_seq = []
        for c in seq:
            c.reverse()
            new_seq.append(c)

        self._log.debug('new_seq =')
        for _c in new_seq:
            self._log.debug('  %s', _c)

        return new_seq


if __name__ == '__main__':
    cli()
