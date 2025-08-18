#
# PiServoのサンプル
#
import time
import pigpio
from piservo0 import PiServo

PIN = 17                          # 使用するGPIOピン番号

pi = pigpio.pi()                  # pigpioの初期化
servo = PiServo(pi, PIN)          # サーボモーターの初期化

servo.move_pulse(1000)            # パルス幅2000に動かす
time.sleep(0.5)                   # サーボが動くのを待つ(0.5秒間スリープ)

servo.move_max()                  # パルス幅を最大(2500)にする
time.sleep(0.5)                   # サーボが動くのを待つ(0.5秒間スリープ)

servo.move_pulse_relative(-1000)  # パルス幅を現在値から1000減らす
time.sleep(0.5)                   # サーボが動くのを待つ(0.5秒間スリープ)

servo.off()                       # サーボOFF
pi.stop()                         # pigpioの終了
