#
# (c) 2025 Yoichi Tanibayashi
#
"""API Client."""
import requests

from piservo0 import get_logger


class ApiClient:
    """API Client.

    POST method    
    """

    DEF_URL = "http://localhost:8000/cmd"
    HEADERS = {'content-type': 'application/json'}

    def __init__(self, url=DEF_URL, debug=False) -> None:
        """Constractor."""
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("url=%s", url)

        self.url = url

    def post(self, data_str: str):
        """Send command line string."""

        res = requests.post(self.url, data=data_str, headers=self.HEADERS)
        self.__log.debug("res=%s", res)

        return res
