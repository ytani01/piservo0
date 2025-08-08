#
# (c) 2025 Yoichi Tanibayashi
#
"""str_api_client.py."""
import requests

from piservo0 import get_logger


class StrApiClient:
    """String API Client."""

    TIMEOUT_CONN = 3.0
    TIMEOUT_READ = 10.0
    TIMEOUT_PARAM = (TIMEOUT_CONN, TIMEOUT_READ)

    def __init__(self, host="localhost", port=8000, debug=False):
        """ constractor """

        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("host=%s, port=%s", host, port)

        self.host = host
        self.port = port

    def make_top_url(self, protocol="http"):
        """ make top URL """

        _url = f"{protocol}://{self.host}:{self.port}/"
        self.__log.debug("url=%s", _url)

        return _url

    def make_cmd_url(self, cmdline):
        """ make URL """
        self.__log.debug("cmdline=%s", cmdline)

        if isinstance(cmdline, (list, tuple)):
            cmdline = " ".join(cmdline)
            self.__log.debug("cmdline=%s", cmdline)

        _url = self.make_top_url() + "cmd/" + cmdline
        self.__log.debug("url=%s", _url)

        return _url

    def url_get(self, url):
        """ get """
        self.__log.debug("url=%s", url)

        try:
            _res = requests.get(url, timeout=self.TIMEOUT_PARAM)
            self.__log.debug("%s:%s> %s", self.host, self.port, _res.json())

        except Exception as _e:
            self.__log.warning("%s: %s", type(_e).__name__, _e)
            raise _e

        return _res

    def send_cmd(self, cmdline):
        """ make URL and send """
        self.__log.debug("cmdline=%a", cmdline)

        return self.url_get(self.make_cmd_url(cmdline))
