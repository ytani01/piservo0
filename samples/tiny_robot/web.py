#
# (c) 2025 Yoichi Tanibayashi
#
"""
  Usage

    cd ~/work/piservo0
    uv pip install -e '.[samples]'
  
    uv run uvicorn samples.tiny_robot.web:app --reload --host 0.0.0.0
  
"""
from os.path import expanduser

import pigpio
from fastapi import FastAPI

from piservo0 import MultiServo, StrControl, ThreadWorker

PINS = [17, 27, 22, 25]
ANGLE_FACTOR = [-1, -1, 1, 1]

CONF_FILE = expanduser("~/servo.json")

print(f"__name__={__name__}")

pi = pigpio.pi()
mservo = MultiServo(pi, PINS, conf_file=CONF_FILE, debug=False)
str_ctrl = StrControl(mservo, angle_factor=ANGLE_FACTOR, debug=False)
thr_worker = ThreadWorker(mservo, debug=True)
thr_worker.start()
    
app = FastAPI()


def run_cmds(cmds: str):
    """ run command string """
    print(f"cmds={cmds}")

    for _cmd in cmds.split():
        print(f"_cmd={_cmd}")

        parsed_cmd = str_ctrl.parse_cmd(_cmd)
        print(f"parsed_cmd={parsed_cmd}")

        thr_worker.send(parsed_cmd)


# 以下のコードを追加するfccc fbbb cbbb ccbb cfbb cfbc bccc cccc cccf bbbf bbbc bbcc bbfc cbfc cccb cccc
@app.get("/")
async def read_root():
    """ root """
    return {"Hello": "World"}

@app.get("/cmd/{cmdline}")
async def exec_cmd(cmdline: str):
    """ execute commands """
    print(f"cmdline='{cmdline}'")

    for cmd in cmdline.split():
        print(f"cmd='{cmd}'")

        if cmd[0] == 'S':
            thr_worker.cmdq_clear()
            continue
 
        run_cmds(cmd)

    return {"cmdline": cmdline}

@app.get("/stop")
async def stop_cmd():
    """ stop and end motion """
    thr_worker.cmdq_clear()

    _end_cmds = "0.5 cccc 0.5 cFFc"
    run_cmds(_end_cmds)
