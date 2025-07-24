#
# (c) 2025 Yoichi Tanibayashi
#
import time

import click

from piservo0 import get_logger

from .tiny_robot_app import TinyRobotApp


@click.command(
   help="""
Tiny Robot Demo #1

`PINS` order:

    PIN1 Front-Left

    PIN2 Back-Left

    PIN3 Back-Right

    PIN4 Front-Rihgt
"""
)
@click.argument("pins", type=int, nargs=4)
@click.option(
    "--count", "-c", type=int, default=10, show_default=True, help="count"
)
@click.option(
    "--angle_unit", "-a", type=float, default=35, show_default=True,
    help="angle Unit",
)
@click.option(
    "--move_sec", "-s", type=float, default=0.2, show_default=True,
    help="move steop sec",
)
@click.option(
    "--step_n", "-n", type=int, default=50, show_default=True,
    help="move steop sec",
)
@click.option(
    "--interval_sec", "-i", type=float, default=0.0, show_default=True,
    help="step interval sec",
)
@click.option(
    "--conf_file", "-f", type=str, default="./servo.json", show_default=True,
    help="Config file path",
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
def demo1(
    pins, count, angle_unit, move_sec, step_n, interval_sec, conf_file, debug
):
    """Tiny Robot Demo #1"""
    __log = get_logger(__name__, debug)
    __log.debug("pins=%s, count=%s", pins, count)
    __log.debug(
        "angle_unit=%s, move_sec=%s, step_n=%s, interval_sec=%s",
        angle_unit, move_sec, step_n, interval_sec
    )
    __log.debug("conf_file=%s", conf_file)

    app = Demo1App(
        pins, count,
        angle_unit, move_sec, step_n, interval_sec, conf_file,
        debug=debug
    )
    app.start()


class Demo1App(TinyRobotApp):
    """Tiny Robot Demo #1"""

    # コマンドシーケンス
    #
    # - [Front-Left, Back-Left, Back-Right, Front-Right]
    # - ここでは、プラスの角度が前方向になるように書く。
    # - F:前、C:中央、B:後
    #
    # (左右反転パターンは、flip_cmds()で生成できる)
    #
    CMDS = [
        "fccc",
        "cbbb",
        ".c..",
        ".f..",
        ".f.c",
        "bcc.",
        "c...",
    ]

    def __init__(
        self, pins, count,
        angle_unit, move_sec, step_n, interval_sec, conf_file,
        debug=False
    ):
        """constractor"""
        super().__init__(
            pins, conf_file, angle_unit, move_sec, step_n, debug=debug
        )
        self.__log = get_logger(__class__.__name__, self._debug)
        self.__log.debug(
            "count=%s, interval_sec=%s", count, interval_sec
        )

        self.count = count
        self.interval_sec = interval_sec

    def main(self):
        """main function"""
        self.__log.debug("")

        _cmds = self.CMDS + self.str_ctrl.flip_cmds(self.CMDS)

        try:
            for _count in range(self.count):
                print(f"===== count={_count}")

                for angles_str in _cmds:
                    print(f" {angles_str}")

                    self.str_ctrl.exec_cmd(angles_str)

                    time.sleep(self.interval_sec)

        except KeyboardInterrupt as _e:
            self.__log.warning("%s", type(_e).__name__)

    def end(self):
        """end: post-processing"""
        self.__log.debug("")
        self.str_ctrl.set_move_sec(1)
        self.str_ctrl.exec_cmd("fbbf")
        self.str_ctrl.exec_cmd("cccc")
        self.str_ctrl.exec_cmd(".5")
        self.str_ctrl.exec_cmd("cFFc")
        super().end()
