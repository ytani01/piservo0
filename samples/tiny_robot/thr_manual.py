#
# (c) 2025 Yoichi Tanibayashi
#
"""

** DEPRECATED **

Itegrated to manual.py

"""
import click

from piservo0 import ThreadWorker, get_logger

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
    "--conf_file", "-f", type=str, default="./servo.json", show_default=True,
    help="Config file path"
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
def thr_manual(
    pins, angle_unit, move_sec, step_n, interval_sec, conf_file, debug
):
    """Tiny Robot manual mode (Thread version)"""

    __log = get_logger(__name__, debug)

    _fmt = "pins=%s,angle_unit=%s,move_sec=%s,step_n=%s,"
    _fmt += "interval_sec=%s,conf_file=%s"
    __log.debug(
        _fmt,
        pins, angle_unit, move_sec, step_n, interval_sec, conf_file
    )

    app = ThrManualApp(
        pins, angle_unit, move_sec, step_n, interval_sec, conf_file,
        debug=debug
    )
    app.start()


class ThrManualApp(TinyRobotApp):
    """Tiny Robot Manual Mode (Thread version)"""

    def __init__(
        self, pins,
        angle_unit, move_sec, step_n, interval_sec, conf_file,
        debug=False
    ):
        """constractor"""
        super().__init__(
            pins, conf_file, angle_unit, move_sec, step_n, debug=debug
        )
        self.__log = get_logger(__class__.__name__, self._debug)
        self.__log.debug("interval_sec=%s", interval_sec)

        self.interval_sec = interval_sec

        self.worker = None

    def init(self):
        """init"""
        super().init()

        self.__log.debug("")

        self.worker = ThreadWorker(
            self.mservo, self.move_sec, self.step_n,
            self.interval_sec, debug=self._debug
        )
        self.worker.start()

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
                    res = self.str_ctrl.parse_cmd(_cmd)
                    self.__log.debug("res=%s", res)

                    if res["cmd"] == "error":
                        self.__log.error('"%s": %s', _cmd, res["msg"])
                        continue

                    self.worker.send(res)

        except (EOFError, KeyboardInterrupt):
            self.__log.info("End of Input")

    def end(self):
        """end: post-processing"""
        self.__log.debug("")
        self.worker.end()
        super().end()
