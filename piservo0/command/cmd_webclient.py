#
# (c) 2025 Yoichi Tanibayashi
#
import json
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

    def __init__(self, host, port, cmdline="", debug=False):
        """ constractor """

        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("host=%s, port=%s", host, port)
        self.__log.debug("cmdline=%a", cmdline)

        self.host = host
        self.port = port
        self.cmdline = cmdline

        self._history_file = os.path.expanduser(self.HISTORY_FILE)

    def make_url_and_send_cmd(self, cmdline):
        """ make URL and send """
        self.__log.debug("cmdline=%a", cmdline)

        _url = f"http://{self.host}:{self.port}/cmd/{cmdline}"
        self.__log.debug("url=%s", _url)

        try:
            _res = requests.get(_url, timeout=self.TIMEOUT_PARAM)
            print(f"{self.host}:{self.port}> {_res.json()}")

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return False

        return True

    def main(self):
        """ main loop """

        # check server
        try:
            _url = f"http://{self.host}:{self.port}/"
            _res = requests.get(_url, timeout=self.TIMEOUT_PARAM)
            print(f"{self.host}:{self.port}> {_res.json()}")

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        # send cmdline
        if self.cmdline:
            self.make_url_and_send_cmd(self.cmdline)
            return

        # interactive mode

        # read history file
        try:
            readline.read_history_file(self._history_file)
            print(f"* history file: {self._history_file}")
            self.__log.debug(
                "history_length=%s", readline.get_current_history_length()
            )

        except FileNotFoundError:
            self.__log.debug("no history file: %s", self._history_file)

        # start interactive mode
        print("* Ctrl-C (Interrput) or Ctrl-D (EOF) for quit")

        while True:
            try:
                _line = input(self.PROMPT_STR)
                readline.write_history_file(self._history_file)

            except (KeyboardInterrupt, EOFError):
                break

            self.make_url_and_send_cmd(_line)

    def end(self):
        """ end """
        print("\n* Bye")
