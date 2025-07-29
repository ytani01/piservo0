#
# (c) 2025 Yoichi Tanibayashi
#
import os
import readline  # input()でヒストリー機能が使える

import requests

from ..utils.my_logger import get_logger


class WebClientApp:
    """ WebClientApp """

    HISTORY_FILE = "~/.piservo0_webclient_history"
    PROMPT_STR = "> "

    TIMEOUT_CONN = 3.0
    TIMEOUT_READ = 10.0
    TIMEOUT_PARAM = (TIMEOUT_CONN, TIMEOUT_READ)

    def __init__(self, host, port, debug=False):
        """ constractor """

        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("host=%s, port=%s", host, port)

        self.host = host
        self.port = port

        self._history_file = os.path.expanduser(self.HISTORY_FILE)

    def main(self):
        """ main loop """
        try:
            _url = f"http://{self.host}:{self.port}/"
            _res = requests.get(_url, timeout=self.TIMEOUT_PARAM)
            print(f"* {self.host}:{self.port} --> {_res.json()}")

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

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
                readline.write_history_file(self._history_file)

                _url = f"http://{self.host}:{self.port}/cmd/{_line}"
                self.__log.debug("url=%s", _url)

                _res = requests.get(_url, timeout=self.TIMEOUT_PARAM)
                print(f"* {_res.json()}")

            except (KeyboardInterrupt, EOFError):
                break

    def end(self):
        """ end """
        print("\n* Bye")
