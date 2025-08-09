#
# (c) 2025 Yoichi Tanibayashi
#
"""json_api_client.py."""

import requests

from piservo0 import get_logger


class JsonApiClient:
    """JSON API Client."""

    DEF_URL = "http://localhost:8000/cmd"
    HEADER = {'content-type': 'application/json'}

    TIMEOUT_CONN = 3.0
    TIMEOUT_READ = 10.0
    TIMEOUT_PARAM = (TIMEOUT_CONN, TIMEOUT_READ)

    def __init__(self, url=DEF_URL, debug=False):
        """constractor"""

        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("url=%s", url)

        self.url = url

    def post_cmd(self, cmd):
        """POST string command"""

        _json_str = str_to_json(cmd)
        self.__log.debug("cmd=%s, json_str=%s", cmd, _json_str)

        try:
            _res = requests.post(self.url, _json_str, headers=self.HEADER)
            self.__log.debug("_res=%s", _res)

        except Exception as _e:
            self.__log.warning("%s: %s", type(_e).__name__, _e)
            raise _e

        return _res
