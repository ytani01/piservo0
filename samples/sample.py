from time import sleep
import pigpio
from piservo0 import PiServo

pi = pigpio.pi()
if not pi.connected:
    exit()

# GPIO 18番ピンに接続されたサーボを操作する
servo = PiServo(pi, 18, debug=True)

try:
    # 中央位置に移動
    servo.center()
    sleep(1)

    # 最小位置に移動
    servo.min()
    sleep(1)

    # 最大位置に移動
    servo.max()
    sleep(1)

    #
    servo.move(975)
    sleep(1)

    #
    servo.move(1925)
    sleep(1)

    # 中央位置に移動
    servo.move(PiServo.CENTER)
    sleep(1)

finally:
    # サーボの電源をオフにする
    servo.off()
    pi.stop()
