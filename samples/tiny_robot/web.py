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

from fastapi import FastAPI

from piservo0 import MultiServo, StrControl

PINS = [17, 27, 23, 25]
CONF_FILE = "/home/ytani/servo.json"
ANGLE_FACTOR = [-1, -1, 1, 1]

pi = pigpio.pi()
mservo = MultiServo(pi, [17, 27, 23, 25], conf_file=CONF_FILE, debug=True)
str_ctrl = StrControl(mservo, angle_factor=ANGLE_FACTOR, debug=True)
    
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
        str_ctrl.exec_cmd(cmd)

    return {"cmdline": cmdline}
