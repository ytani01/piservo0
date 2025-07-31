#
# (c) 2025 Yoichi Tanibayashi
#
"""
  Usage

    cd ~/work/piservo0
    uv pip install -e '.[samples]'

    uv run uvicorn samples.tiny_robot.web:app --reload --host 0.0.0.0

"""
from contextlib import asynccontextmanager
from os.path import expanduser

import pigpio
from fastapi import FastAPI, Request

from piservo0 import MultiServo, StrControl, ThreadWorker

# --- Constants ---
PINS = [17, 27, 22, 25]
ANGLE_FACTOR = [-1, -1, 1, 1]
CONF_FILE = expanduser("~/servo.json")

# Motion Commands
FORWARD_CMDS = (
    "cccc fccc fbbb cbbb ccbb cfbb cfbc bccc "
    "cccc cccf bbbf bbbc bbcc bbfc cbfc cccb"
)
RIGHT_CMDS = (
    "cccc bbff bbFf fbFf fbfF cbcF cfcF bFcc "
    "bFcb bfbb bcBc fcBc fcbc Fccc Fcbc fcbc fcbB"
)
LEFT_CMDS = (
    "cccc ffbb fFbb fFbf Ffbf Fcbc Fcfc ccFb "
    "bcFb bbfb cBcb cBcf cbcf cccF cbcF cbcf Bbcf"
)
STOP_CMDS = "0.5 cccc 0.5 cFFc"

print(f"__name__={__name__}")


# --- Main Application Class ---
class TinyRobotWebApp:
    """Main class for the Tiny Robot Web Application"""

    def __init__(self):
        print("Initializing TinyRobotWebApp...")
        self.pi = pigpio.pi()
        self.mservo = MultiServo(
            self.pi, PINS, conf_file=CONF_FILE, debug=False
        )
        self.str_ctrl = StrControl(
            self.mservo, angle_factor=ANGLE_FACTOR, debug=False
        )
        self.thr_worker = ThreadWorker(self.mservo, debug=True)

    def startup(self):
        """Start the worker thread"""
        print("Starting worker thread...")
        self.thr_worker.start()

    def shutdown(self):
        """Stop threads and cleanup resources"""
        print("Shutting down...")
        self.thr_worker.end()
        self.thr_worker.join()
        self.pi.stop()
        print("Cleanup complete.")

    def send_cmd_str(self, cmds: str):
        """Parse a command string and send commands to the worker thread."""
        print(f"cmds='{cmds}'")
        for cmd in cmds.split():
            print(f"cmd='{cmd}'")
            if cmd.upper() == "S":
                self.thr_worker.clear_cmdq()
                continue

            parsed_cmd = self.str_ctrl.parse_cmd(cmd)
            print(f"parsed_cmd={parsed_cmd}")
            self.thr_worker.send(parsed_cmd)

    def stop_and_repeat_cmd(self, cmds: str, n: int = 50):
        """Clear the command queue and repeat a command string."""
        print(f"Repeating cmds='{cmds}' for {n} times")
        self.thr_worker.clear_cmdq()
        repeated_cmds = cmds * n
        self.send_cmd_str(repeated_cmds)

    def stop(self):
        """Stop motion and run stop commands."""
        self.thr_worker.clear_cmdq()
        self.send_cmd_str(STOP_CMDS)


# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for the application"""
    robot_app = TinyRobotWebApp()
    robot_app.startup()
    app.state.robot_app = robot_app
    yield
    app.state.robot_app.shutdown()


app = FastAPI(lifespan=lifespan)


# --- API Endpoints ---
@app.get("/")
async def read_root():
    """root"""
    return {"Hello": "World"}


@app.get("/cmd/{cmdline}")
async def exec_cmd(request: Request, cmdline: str):
    """execute commands"""
    print(f"cmdline='{cmdline}'")
    request.app.state.robot_app.send_cmd_str(cmdline)
    return {"cmdline": cmdline}


@app.get("/forward")
async def forward_cmd(request: Request):
    """walk forward"""
    request.app.state.robot_app.stop_and_repeat_cmd(FORWARD_CMDS)
    return {"status": "walking forward"}


@app.get("/right")
async def right_cmd(request: Request):
    """turn right"""
    request.app.state.robot_app.stop_and_repeat_cmd(RIGHT_CMDS)
    return {"status": "turning right"}


@app.get("/left")
async def left_cmd(request: Request):
    """turn left"""
    request.app.state.robot_app.stop_and_repeat_cmd(LEFT_CMDS)
    return {"status": "turning left"}


@app.get("/stop")
async def stop_cmd(request: Request):
    """stop and end motion"""
    request.app.state.robot_app.stop()
    return {"status": "stopping"}
