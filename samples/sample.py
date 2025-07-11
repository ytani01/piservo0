import time
from piservo0 import PiServo

# GPIO 18番ピンに接続されたサーボを操作する
servo = PiServo(18, debug=True)

try:
    # 中央位置に移動
    servo.move(PiServo.PULSE_CENTER)
    time.sleep(1)

    # 最小位置に移動
    servo.move(PiServo.PULSE_MIN)
    time.sleep(1)

    # 最大位置に移動
    servo.move(PiServo.PULSE_MAX)
    time.sleep(1)

    # 中央位置に移動
    servo.move(PiServo.PULSE_CENTER)
    time.sleep(1)

finally:
    # サーボの電源をオフにする
    servo.off()
