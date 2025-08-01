#
# (c) 2025 Yoichi Tanibayashi
#
"""
piservo0 String API Server
"""
import os
from contextlib import asynccontextmanager

import pigpio
from fastapi import FastAPI, Request

from piservo0 import StrControl, ThreadMultiServo, get_logger


class StrApi:
    """Main class for Web Application"""

    def __init__(self, pins, angle_factor, debug=False):
        """ constractor """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)

        self.pins = pins
        self.angle_factor = angle_factor

        self.__log.debug(
            "pins=%s, angle_factor=%s", self.pins, self.angle_factor
        )

        print("Initializing ...")
        self.pi = pigpio.pi()
        self.mservo = ThreadMultiServo(
            self.pi, self.pins, debug=False
        )
        self.str_ctrl = StrControl(
            self.mservo, angle_factor=self.angle_factor, debug=False
        )

    def end(self):
        """ end """
        self.mservo.end()

    def exec_cmdline(self, cmdline):
        """ execute command line """
        self.__log.info("cmdline=%s", cmdline)

        _res = self.str_ctrl.exec_multi_cmds(cmdline)
        self.__log.info("_res=%s", _res)

        return _res


# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for the application"""

    # --- get options from envron variables ---
    pins_str = str(os.getenv("PISERVO0_PINS"))
    pins = [int(p.strip()) for p in pins_str.split(",")]

    angle_factor_str = str(os.getenv("PISERVO0_ANGLE_FACTOR"))
    angle_factor = [int(f.strip()) for f in angle_factor_str.split(",")]

    debug_str = os.getenv("PISERVO0_DEBUG", "0")
    debug = debug_str == "1"

    log = get_logger(__name__, debug)
    log.debug(
        "pins=%s, angle_factor=%s, debug=%s", pins, angle_factor, debug
    )

    # --- make 'webapp' ---
    app.state.webapp = StrApi(pins, angle_factor, debug=debug)

    yield

    app.state.webapp.end()


# --- make 'app' ---
app = FastAPI(lifespan=lifespan)


# --- API Endpoints ---
@app.get("/")
async def read_root():
    """root"""
    return {"Hello": "World"}


@app.get("/cmd/{cmdline}")
async def exec_cmd(request: Request, cmdline: str):
    """execute commands"""

    _res = request.app.state.webapp.exec_cmdline(cmdline)
    print(f"_res={_res}")

    return _res
