import time
import pigpio
from piservo0 import CalibrableServo

# pigpio.piのインスタンスを生成
pi = pigpio.pi()
if not pi.connected:
    exit()

# GPIO 18番ピンに接続されたサーボを操作
# キャリブレーションデータは 'servo.json' に保存されます
servo = CalibrableServo(pi, 18, debug=True)

try:
    # --- パルスをしていして移動 ---
    print("Move by pulse")
    servo.move_pulse(1000)
    time.sleep(1)
    servo.move_pulse(2000)
    time.sleep(1)

    # --- キャリブレーションされた位置へ移動 ---
    print("Move to calibrated positions")
    servo.move_min()
    time.sleep(1)
    servo.move_max()
    time.sleep(1)
    servo.move_center()
    time.sleep(1)

    # --- 角度を指定して移動 ---
    print("Move by angle")
    servo.move_angle(-90)
    time.sleep(1)
    servo.move_angle(90)
    time.sleep(1)
    servo.move_angle(0)
    time.sleep(1)

finally:
    # サーボの電源をオフにする
    servo.off()
    pi.stop()
