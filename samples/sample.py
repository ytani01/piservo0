import time
import pigpio
from piservo0 import PiServo

pi = pigpio.pi()
if not pi.connected:
    exit()

# GPIO 18番ピンに接続されたサーボを操作する
servo = PiServo(pi, 18, debug=True)

try:
    # 中央位置に移動
    servo.move(PiServo.CENTER)
    time.sleep(1)

    # 最小位置に移動
    servo.move(PiServo.MIN)
    time.sleep(1)

    # 最大位置に移動
    servo.move(PiServo.MAX)
    time.sleep(1)

    # 中央位置に移動
    servo.move(PiServo.CENTER)
    time.sleep(1)

finally:
    # サーボの電源をオフにする
    servo.off()
    pi.stop()
