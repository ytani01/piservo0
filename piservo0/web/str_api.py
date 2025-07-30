#
# (c) 2025 Yoichi Tanibayashi
#
"""
  Usage

    cd ~/work/piservo0
    uv pip install -e .

    uv run uvicorn piservo0.web.str_api:app --reload --host 0.0.0.0

"""
from contextlib import asynccontextmanager

import pigpio
from fastapi import FastAPI, Request

from piservo0 import StrControl, ThreadMultiServo, get_logger

# --- Constants ---
PINS = [17, 27, 22, 25]
ANGLE_FACTOR = [-1, -1, 1, 1]


class StrApi:
    """Main class for Web Application"""

    def __init__(self, debug=False):
        """ constractor """
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        
        print("Initializing ...")
        self.pi = pigpio.pi()
        self.mservo = ThreadMultiServo(self.pi, PINS, debug=False)
        self.str_ctrl = StrControl(self.mservo, debug=False)

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

    app.state.webapp = StrApi()

    yield

    app.state.webapp.end()


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
