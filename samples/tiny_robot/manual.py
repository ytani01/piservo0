#
# (c) 2025 Yoichi Tanibayashi
#
import time

import click

from piservo0 import get_logger

from .tiny_robot_app import TinyRobotApp


@click.command(
    help="""
Tiny Robot: Manual mode

`PINS` order:

    PIN1 Front-Left

    PIN2 Back-Left

    PIN3 Back-Right

    PIN4 Front-Rihgt
"""
)
@click.argument("pins", type=int, nargs=4)
@click.option(
    "--angle_unit", "-a", type=float, default=35, show_default=True,
    help="angle Unit"
)
@click.option(
    "--move_sec", "-s", type=float, default=0.2, show_default=True,
    help="move steop sec"
)
@click.option(
    "--step_n", "-n", type=int, default=50, show_default=True,
    help="move steop sec",
)
@click.option(
    "--interval_sec", "-i", type=float, default=0.0, show_default=True,
    help="step interval sec"
)
@click.option(
    "--thread", "-t", is_flag=True, help="Multi Thread Version"
)
@click.option(
    "--conf_file", "-f", type=str, default="./servo.json", show_default=True,
    help="Config file path"
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
def manual(
    pins, angle_unit, move_sec, step_n, interval_sec, conf_file,
    thread, debug
):
    """Tiny Robot manual mode"""

    __log = get_logger(__name__, debug)

    __log.debug("pins=%s", pins)
    __log.debug(
        "angle_unit=%s, move_sec=%s, step_n=%s, interval_sec=%s",
        angle_unit, move_sec, step_n, interval_sec
    )
    __log.debug("thread=%s", thread)
    __log.debug("conf_file=%s", conf_file)

    app = ManualApp(
        pins, angle_unit, move_sec, step_n, interval_sec, conf_file,
        thread, debug=debug
    )
    app.start()


class ManualApp(TinyRobotApp):
    """Tiny Robot Manual Mode"""

    def __init__(
        self, pins, angle_unit, move_sec, step_n, interval_sec, conf_file,
        thread=False, debug=False
    ):
        """constractor"""
        super().__init__(
            pins, conf_file, angle_unit, move_sec, step_n, thread, debug=debug
        )
        self.__log = get_logger(__class__.__name__, self._debug)
        self.__log.debug("interval_sec=%s", interval_sec)

        self.interval_sec = interval_sec

    def main(self):
        """main function"""
        self.__log.debug("")

        try:
            while True:
                line = input("> ")
                if not line:
                    break

                cmds = line.split()
                self.__log.debug("cmds=%s", cmds)

                for _cmd in cmds:
                    print(f" {_cmd}")

                    self.str_ctrl.exec_cmd(_cmd)

                    time.sleep(self.interval_sec)

        except (EOFError, KeyboardInterrupt):
            self.__log.info("End of Input")
