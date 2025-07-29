#
# (c) 2025 Yoichi Tanibayashi
#
import readline  # importするだけで、input()でヒストリー機能が使える

from ..helper.str_control import StrControl
from ..helper.thread_multi_servo import ThreadMultiServo
from ..utils.my_logger import get_logger


class StrCtrlApp:
    """ StrCtrlApp """

    BS_KEYS = [
        "KEY_BACKSPACE",
        "KEY_DELETE",
    ]

    PROMPT_STR = "> "

    def __init__(
        self, pi, pins, conf_file,
        move_sec, step_n, angle_unit, angle_factor,
        debug
    ):
        """ constractor """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("pins=%s, conf_file=%s", pins, conf_file)

        self._mservo = ThreadMultiServo(
            pi, pins, conf_file=conf_file, debug=self._debug
        )
        self._str_ctrl = StrControl(
            self._mservo,
            move_sec, step_n, angle_unit, angle_factor,
            debug=self._debug
        )

        readline.clear_history()  # dummy for linter

    def main(self):
        """ main loop """
        print("Start -- Ctrl-C (Interrput) or Ctrl-D (EOF) for quit")

        while True:
            try:
                _line = input(self.PROMPT_STR)
                self._str_ctrl.exec_multi_cmds(_line)

            except (KeyboardInterrupt, EOFError):
                break

    def end(self):
        """ end """
        print("\nBye")
        self._mservo.end()
