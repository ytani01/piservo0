# GPIO17に接続されたサーボをパルス幅で動かす例
import time
import pigpio
from piservo0 import PiServo

pi = pigpio.pi()         # pigpioの初期化
servo = PiServo(pi, 17)  # GPIO17に接続されたサーボモーターの初期化

servo.move_pulse(2000)   # パルス幅2000に動かす
time.sleep(0.5)          # サーボが動くのを待つ(0.5秒間スリープ)

servo.move_pulse(1000)   # パルス幅1000に動かす
time.sleep(0.5)          # サーボが動くのを待つ(0.5秒間スリープ)

servo.off()              # サーボOFF
pi.stop()                # pigpioの終了
