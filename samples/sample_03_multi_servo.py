#
# MultiServoのサンプル
#
import time
import pigpio
from piservo0 import MultiServo

PINS = [17, 27, 22]             # 3つのサーボを使う

pi = pigpio.pi()                # pigpioの初期化
servos = MultiServo(pi, PINS)   # 全サーボの初期化
time.sleep(1)                   # 初期化時にすべて0度に揃える

for angles in [                 # 各サーボの角度を連続指定
        [  0,   0,   0],
        [ 90,  45,  30],
        [  0,  90,  60],
        [-90,  45,  90],
        [  0,   0,  60],
        [ 90, -45,  30],
        [  0, -90,   0],
        [-90, -45, -30],
        [  0,   0, -60],
        [ 90,  45, -90],
        [  0,  90, -60],
        [-90,  45, -30],
        [  0,   0,   0],
]:
    servos.move_all_angles_sync(angles) # すべてのサーボを同期して動かす

servos.off()                            # 全サーボOFF 
pi.stop()                               # piservo 終了処理
