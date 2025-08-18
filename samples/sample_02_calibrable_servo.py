#
# CalibrableServoのサンプル
#
import time
import pigpio
from piservo0 import CalibrableServo

PIN1 = 17                         # 使用するGPIOピン番号

pi = pigpio.pi()                  # pigpioの初期化
servo = CalibrableServo(pi, PIN1) # サーボモーターの初期化

servo.move_angle(-60)             # 角度を(中央から)-60度に動かす
time.sleep(0.5)                   # サーボが動くのを待つ

servo.move_max()                  # 最大角度(90度)に動かす
time.sleep(0.5)                   # サーボが動くのを待つ

servo.move_angle_relative(-60)    # 現在値から相対的に-60度動かす
time.sleep(0.5)                   # サーボが動くのを待つ

servo.off()                       # サーボOFF
pi.stop()                         # pigpioの終了
