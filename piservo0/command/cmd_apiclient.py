
#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apiclient.py"""
import os
import readline  # input()でヒストリー機能が使える

from piservo0 import ApiClient, get_logger


class CmdApiClient:
    """CmdApiClient."""

    PROMPT_STR = "> "

    def __init__(self, cmd_name, url, cmdline, history_file, debug=False):
        """constractor."""
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("cmd_name=%s, url=%s", cmd_name, url)
        self.__log.debug("cmdline=%a", cmdline)

        self.cmd_name = cmd_name
        self.url = url
        self.cmdline = cmdline
        self.history_file = os.path.expanduser(history_file)

        self.api_client = ApiClient(self.url, self._debug)

    def print_response(self, _res):
        """print response in json format"""
        print(f"* {self.url}> {_res.json()}")

    def parse_cmdline(self, cmdline):
        """parse command line string to json

        *** To Be Override ***

        """
        return cmdline

    def main(self):
        """main loop"""

        if self.cmdline:
            #
            # command arguments mode
            #
            for _l in self.cmdline.split():
                self.__log.debug("_l=%s", _l)

                _parsed_line = self.parse_cmdline(_l)
                _res = self.api_client.post(_parsed_line)
                self.print_response(_res)
            return

        #
        # interactive mode
        #
        try:
            # read history file
            readline.read_history_file(self.history_file)
            print(f"* history file: {self.history_file}")
            self.__log.debug(
                "history_length=%s",
                readline.get_current_history_length()
            )

        except FileNotFoundError:
            self.__log.debug("no history file: %s", self.history_file)

        # start interactive mode
        print("* Ctrl-C (Interrput) or Ctrl-D (EOF) for quit")

        while True:
            try:
                _line = input(self.cmd_name + self.PROMPT_STR)
                self.__log.debug("_line=%s", _line)
                readline.write_history_file(self.history_file)

            except (KeyboardInterrupt, EOFError):
                break

            _parsed_line = self.parse_cmdline(_line)
            _res = self.api_client.post(_parsed_line)
            self.print_response(_res)

    def end(self):
        """end"""
        print("\n* Bye\n")
