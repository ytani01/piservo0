#
# (c) 2025 Yoichi Tanibayashi
#
"""
  Usage

    cd ~/work/piservo0
    uv pip install -e .

    uv run uvicorn piservo.web.api:app --reload --host 0.0.0.0

"""
from contextlib import asynccontextmanager

import pigpio
from fastapi import FastAPI, Request

from piservo0 import StrControl, ThreadMultiServo

# --- Constants ---
PINS = [17, 27, 22, 25]
ANGLE_FACTOR = [-1, -1, 1, 1]


class WepApp:
    """Main class for Web Application"""

    def __init__(self):
        """ constractor """
        print("Initializing WepApp...")
        self.pi = pigpio.pi()
        self.mservo = ThreadMultiServo(self.pi, PINS, debug=False)
        self.str_ctrl = StrControl(self.mservo, debug=False)

    def end(self):
        """ end """
        self.mservo.end()

    def exec_cmd(self, cmdline):
        """ execute command line """
        self.str_ctrl.exec_multi_cmds(cmdline)

# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for the application"""

    app.state.webapp = WepApp()

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

    _ret = request.app.state.webapp.str_ctrl.exec_multi_cmds(cmdline)

    return _ret
