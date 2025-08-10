#
# (c) 2025 Yoichi Tanibayashi
#
"""
piservo0 JSON API Server
"""
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Union

import pigpio
from fastapi import Body, FastAPI, Request

from piservo0 import MultiServo, ThreadWorker, get_logger


class JsonApi:
    """Main class for Web Application"""

    def __init__(self, pins, debug=False):
        """constractor"""
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)

        self.pins = pins

        self.__log.debug("pins=%s", self.pins)

        print("Initializing ...")
        self.pi = pigpio.pi()

        self.mservo = MultiServo(self.pi, self.pins) #  debug=self._debug)
        self.thr_worker = ThreadWorker(self.mservo, debug=self._debug)
        self.thr_worker.start()

    def end(self):
        """end"""
        self.thr_worker.end()

    def send_cmdjson(self, cmdjson):
        """send JSON command to thread worker"""
        self.__log.debug("cmdjson=%s", cmdjson)

        _res = self.thr_worker.send(cmdjson)

        return _res


# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for the application"""

    # --- get options from envron variables ---
    pins_str = str(os.getenv("PISERVO0_PINS"))
    pins = [int(p.strip()) for p in pins_str.split(",")]

    debug_str = os.getenv("PISERVO0_DEBUG", "0")
    debug = debug_str == "1"

    log = get_logger(__name__, debug)
    log.debug("pins=%s, debug=%s", pins, debug)

    app.state.json_app = JsonApi(pins, debug=debug)
    app.state.debug = debug

    yield

    app.state.json_app.end()


# --- make 'app' ---
app = FastAPI(lifespan=lifespan)


# --- API Endpoints ---
@app.get("/")
async def read_root():
    """root"""
    return {"Hello": "World"}


@app.post("/cmd")
async def exec_cmd(
    request: Request,
    cmd: Union[List[Dict[str, Any]], Dict[str, Any]] = Body()
):
    """execute commands.

       JSON配列を受け取り、コマンドを実行する。
    """
    debug = request.app.state.debug
    _log = get_logger(__name__, debug)
    _log.debug("cmd=%s, type=%s", cmd, type(cmd))

    cmd_list: List[Dict[str, Any]]
    if isinstance(cmd, dict):
        cmd_list = [cmd]
    else:
        cmd_list = cmd

    _log.debug("cmd_list=%s", cmd_list)

    _json_app = request.app.state.json_app
    _res = []
    for c in cmd_list:
        _res1 = _json_app.send_cmdjson(c)
        _log.debug("c=%s, _res1=%s", c, _res1)
        _res.append(_res1)

    _log.debug("_res=%s", _res)
    return _res
