#
# (c) 2025 Yoichi Tanibayashi
#
import time

import click

from piservo0 import get_logger

from .thr_worker import ThrWorker
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
    "--angle_unit",
    "-a",
    "-u",
    type=float,
    default=35,
    show_default=True,
    help="angle Unit",
)
@click.option(
    "--move_sec",
    "-s",
    type=float,
    default=0.2,
    show_default=True,
    help="move steop sec",
)
@click.option(
    "--interval_sec",
    "-i",
    type=float,
    default=0.0,
    show_default=True,
    help="step interval sec",
)
@click.option(
    "--conf_file",
    "-f",
    type=str,
    default="./servo.json",
    show_default=True,
    help="Config file path",
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
def thr_manual(pins, angle_unit, move_sec, interval_sec, conf_file, debug):
    """Tiny Robot manual mode (Thread version)"""

    _log = get_logger(__name__, debug)

    _fmt = "pins=%s,angle_unit=%s,move_sec=%s,"
    _fmt += "interval_sec=%s,conf_file=%s"
    _log.debug(_fmt, pins, angle_unit, move_sec, interval_sec, conf_file)

    app = ThrManualApp(
        pins, angle_unit, move_sec, interval_sec, conf_file, debug=debug
    )
    app.start()


class ThrManualApp(TinyRobotApp):
    """Tiny Robot Manual Mode"""

    def __init__(
        self, pins, angle_unit, move_sec, interval_sec, conf_file, debug=False
    ):
        """constractor"""
        super().__init__(pins, conf_file, debug=debug)

        self._log = get_logger(__class__.__name__, self._debug)
        self._log.debug("angle_unit=%s", angle_unit)
        self._log.debug(
            "move_sec=%s,interval_sec=%s", move_sec, interval_sec
        )

        self.angle_unit = angle_unit
        self.move_sec = move_sec
        self.interval_sec = interval_sec

    def init(self):
        """ init """
        super().init()
        
        self._log.debug("")
        
        self.worker = ThrWorker(
            self.mservo, self.move_sec, self.angle_unit,
            self.interval_sec,
            debug=self._debug
        )
        self.worker.start()

    def main(self):
        """main function"""
        self._log.debug("")

        time.sleep(1.0)

        try:
            while True:
                line = input("> ")
                if not line:
                    break

                self.worker.send(line)

        except (EOFError, KeyboardInterrupt) as _e:
            self._log.info("End of Input")

    def end(self):
        """end: post-processing"""
        self._log.debug("")
        self.worker.end()
        super().end()
