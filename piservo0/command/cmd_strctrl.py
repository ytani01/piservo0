#
# (c) 2025 Yoichi Tanibayashi
#
import os
import readline  # input()でヒストリー機能が使える

from piservo0 import StrControl, ThreadMultiServo, get_logger


class StrCtrlApp:
    """ StrCtrlApp """

    HISTORY_FILE = "~/.piservo0_strctrl_history"
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

        self._history_file = os.path.expanduser(self.HISTORY_FILE)

    def main(self):
        """ main loop """
        try:
            readline.read_history_file(self._history_file)
            print(f"* history file: {self._history_file}")
            self.__log.debug(
                "history_length=%s", readline.get_current_history_length()
            )
        except FileNotFoundError:
            self.__log.debug("no history file: %s", self._history_file)

        print("* Ctrl-C (Interrput) or Ctrl-D (EOF) for quit")

        while True:
            try:
                _line = input(self.PROMPT_STR)
                self._str_ctrl.exec_multi_cmds(_line)
                readline.write_history_file(self._history_file)

            except (KeyboardInterrupt, EOFError):
                break

    def end(self):
        """ end """
        print("\nBye")
        self._mservo.end()
