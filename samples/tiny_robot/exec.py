#
# (c) 2025 Yoichi Tanibayashi
#
import time
import click
from piservo0 import get_logger
from .app import TinyRobotApp


@click.command(help="""
Tiny Robot: Execute Script files

`PINS` order:

    PIN1 Front-Left

    PIN2 Back-Left

    PIN3 Back-Right

    PIN4 Front-Rihgt

One or more `SCRIPT_FILE`s
""")
@click.argument('pins', type=int, nargs=4)
@click.argument('script_file', type=str, nargs=-1)
@click.option('--count', '-c', type=int,
              default=1, show_default=True,
              help='execution count')
@click.option('--angle_unit', '-a', '-u', type=float,
              default=35, show_default=True,
              help='angle Unit')
@click.option('--move_sec', '-s', type=float,
              default=.2, show_default=True,
              help='move steop sec')
@click.option('--interval_sec', '-i', type=float,
              default=0.0, show_default=True,
              help='step interval sec')
@click.option('--conf_file', '-f', type=str,
              default='./servo.json', show_default=True,
              help='Config file path')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
def exec(pins, script_file, count, angle_unit, move_sec, interval_sec, conf_file,
          debug):
    """ Tiny Robot Demo #1 """
    _log = get_logger(__name__, debug)
    _fmt = 'pins=%s,'
    _fmt += 'script_file=%s,'
    _fmt += 'count=%s,angle_unit=%s,move_sec=%s,'
    _fmt += 'interval_sec=%s,conf_file=%s'
    _log.debug(_fmt,
               pins, script_file,
               count, angle_unit, move_sec, interval_sec,
               conf_file)

    app = ExecApp(pins, script_file, count,
                  angle_unit, move_sec, interval_sec,
                  conf_file, debug=debug)
    app.start()


class ExecApp(TinyRobotApp):
    """ Tiny Robot Demo #1
    """

    def __init__(self, pins, script_file,
                 count, angle_unit, move_sec, interval_sec,
                 conf_file, debug=False):
        """ constractor """
        super().__init__(pins, conf_file, debug=debug)
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('script_file=%s', script_file)
        self._log.debug('count=%s, angle_unit=%s', count, angle_unit)
        self._log.debug('move_sec=%s, interval_sec=%s',
                        move_sec, interval_sec)

        self.script_file = script_file
        self.count = count
        self.angle_unit = angle_unit
        self.move_sec = move_sec
        self.interval_sec = interval_sec

    def main(self):
        """ main function """
        self._log.debug('')

        time.sleep(1.0)

        try:
            for _count in range(self.count):
                print(f'===== count={_count}')

                for _file in self.script_file:
                    self._log.debug('_file=%s', _file)

                    with open(_file) as _f:
                        for line in _f:
                            self._log.debug('line=%s', line)

                            cmds = line.split()
                            self._log.debug('cmds=%s', cmds)

                            for cmd in cmds:
                                print(f' {cmd}')

                                self.util.exec_cmd(cmd)

                                time.sleep(self.interval_sec)

        except KeyboardInterrupt as _e:
            self._log.warning('%s', type(_e).__name__)

    def end(self):
        """ end: post-processing """
        self._log.debug("")
        self.util.set_move_sec(0.5)
        self.util.exec_cmd('cccc')
        self.util.set_move_sec(1.5)
        self.util.exec_cmd('cFFc')
        super().end()
