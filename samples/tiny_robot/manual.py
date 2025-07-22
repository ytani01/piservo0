#
# (c) 2025 Yoichi Tanibayashi
#
import sys
import time
import click
from piservo0 import get_logger
from .app import TinyRobotApp


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
def manual(pins, angle_unit, move_sec, interval_sec, conf_file, debug):
    """Tiny Robot manual mode"""
    _log = get_logger(__name__, debug)
    _fmt = "pins=%s,angle_unit=%s,move_sec=%s,"
    _fmt += "interval_sec=%s,conf_file=%s"
    _log.debug(_fmt, pins, angle_unit, move_sec, interval_sec, conf_file)

    app = ManualApp(pins, angle_unit, move_sec, interval_sec, conf_file, debug=debug)
    app.start()


class ManualApp(TinyRobotApp):
    """Tiny Robot Manual Mode"""

    def __init__(
        self, pins, angle_unit, move_sec, interval_sec, conf_file, debug=False
    ):
        """constractor"""
        super().__init__(pins, conf_file, debug=debug)
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug("angle_unit=%s", angle_unit)
        self._log.debug("move_sec=%s,interval_sec=%s", move_sec, interval_sec)

        self.angle_unit = angle_unit
        self.move_sec = move_sec
        self.interval_sec = interval_sec

    def main(self):
        """main function"""
        self._log.debug("")

        time.sleep(1.0)

        try:
            while True:
                line = input("> ")
                if not line:
                    break

                cmds = line.split()
                self._log.debug("cmds=%s", cmds)

                for cmd in cmds:
                    res = self.util.parse_cmd(cmd)

                    if res["cmd"] == "angles":
                        angles = res["angles"]
                        self.mservo.move_angle_sync(angles, self.move_sec)
                        time.sleep(self.interval_sec)

                    if res["cmd"] == "interval":
                        time.sleep(float(res["sec"]))

                    if res["cmd"] == "error":
                        print(f"ERROR: {cmd}: {res['err']}", file=sys.stderr)

        except (EOFError, KeyboardInterrupt):
            self._log.warning("End of Input")

    def end(self):
        """end: post-processing"""
        self._log.debug("")
        super().end()
