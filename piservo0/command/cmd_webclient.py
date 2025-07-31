#
# (c) 2025 Yoichi Tanibayashi
#
""" cmd_webclient.py """
import os
import readline  # input()でヒストリー機能が使える

from piservo0 import StrApiClient, get_logger


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

        self.api_client = StrApiClient(self.host, self.port)

        self._history_file = os.path.expanduser(self.HISTORY_FILE)

    def print_response(self, _res):
        """ print response in json format"""
        print(f"{self.host}:{self.port}> {_res.json()}")

    def main(self):
        """ main loop """

        # check server
        try:
            _url = self.api_client.make_top_url()
            _res = self.api_client.url_get(_url)
            print(f"{self.host}:{self.port}> {_res.json()}")

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        if self.cmdline:
            #
            # send cmdline (1 shot)
            #
            _res = self.api_client.send_cmd(self.cmdline)
            self.print_response(_res)
            return

        #
        # interactive mode
        #

        try:
            # read history file
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

            _res = self.api_client.send_cmd(_line)
            self.print_response(_res)

    def end(self):
        """ end """
        print("\n* Bye\n")
