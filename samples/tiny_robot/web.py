#
# (c) 2025 Yoichi Tanibayashi
#
"""
  Usage

    cd ~/work/piservo0
    uv pip install -e '.[samples]'
  
    uv run uvicorn samples.tiny_robot.web:app --reload --host 0.0.0.0
  
"""
import pigpio

from os.path import expanduser
from fastapi import FastAPI

from piservo0 import MultiServo, StrControl, ThrWorker

PINS = [17, 27, 22, 25]
ANGLE_FACTOR = [-1, -1, 1, 1]

CONF_FILE = expanduser("~/servo.json")

pi = pigpio.pi()
mservo = MultiServo(pi, PINS, conf_file=CONF_FILE, debug=False)
str_ctrl = StrControl(mservo, angle_factor=ANGLE_FACTOR, debug=False)
thr_worker = ThrWorker(mservo, debug=False)
thr_worker.start()
    
app = FastAPI()

# 以下のコードを追加する
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/cmd/{cmdline}")
async def exec_cmd(cmdline: str):
    print(f"cmdline='{cmdline}'")

    for cmd in cmdline.split():
        print(f"cmd='{cmd}'")

        if cmd[0] == 'S':
            thr_worker.cmdq_clear()
            continue

        parsed_cmd = str_ctrl.parse_cmd(cmd)
        print(f"parsed_cmd={parsed_cmd}")
        
        thr_worker.send(parsed_cmd)

    return {"cmdline": cmdline}
