#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_strclient.py."""
from piservo0 import StrCmdToJson, get_logger

from .cmd_apiclient import CmdApiClient


class CmdStrClient(CmdApiClient):
    """CmdStrClient."""

    def __init__(
        self, cmd_name, url, cmdline, history_file, angle_factor, debug=False
    ):
        super().__init__(cmd_name, url, cmdline, history_file, debug)

        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug(
            "cmd_name=%s, angle_factor=%s", cmd_name, angle_factor
        )

        self._angle_factor = angle_factor

        self.parser = StrCmdToJson(self._angle_factor, debug=self._debug)

    def parse_cmdline(self, cmdline):
        """parse string command to json."""
        self.__log.debug("cmdline=%s", cmdline)

        parsed_str = self.parser.jsonstr(cmdline)
        self.__log.debug("parsed_str=%s", parsed_str)

        return parsed_str
