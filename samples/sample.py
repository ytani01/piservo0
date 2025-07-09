import time
from piservo0.pigpio import PiGPIO

# GPIO 18番ピンに接続されたサーボを操作する
servo = PiGPIO(18)

try:
    # 中央位置に移動
    servo.move(PiGPIO.PULSE_CENTER)
    time.sleep(1)

    # 最小位置に移動
    servo.move(PiGPIO.PULSE_MIN)
    time.sleep(1)

    # 最大位置に移動
    servo.move(PiGPIO.PULSE_MAX)
    time.sleep(1)

finally:
    # サーボの電源をオフにする
    servo.off()
