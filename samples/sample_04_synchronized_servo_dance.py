
import time
import math
import pigpio
from piservo0.multi_servo import MultiServo

def synchronized_servo_dance():
    """
    3つのサーボモーターが同期してダンスを踊るデモプログラムである。
    異なる位相でサイン波状に動き、協調性のある動きを表現する。
    """
    print("シンクロナイズド・サーボ・ダンスを開始する。")

    # サーボ設定ファイルのパス
    config_file = "samples/sample_servo.json" # samplesディレクトリのファイルを使用

    # pigpioデーモンに接続
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioデーモンに接続できない。実行前に 'sudo pigpiod' を実行する。")
        return

    # サーボのピン番号を固定する
    servo_pins = [18, 21, 24] # ピン番号18, 21, 24を使用する

    # MultiServoを初期化
    # CalibrableServoが設定ファイルを読み込むため、ここでconfig_fileを渡す
    multi_servo = MultiServo(pi, servo_pins, conf_file=config_file)

    try:
        # デモ実行時間（秒）
        duration = 20

        # 動きのパラメータ
        amplitude = 45  # 角度の振幅（度）
        offset = 0     # 中心角度（度）
        frequency = 0.5 # 動きの周波数（Hz）

        start_time = time.time()
        while (time.time() - start_time) < duration:
            elapsed_time = time.time() - start_time

            # サーボ1の角度計算（位相0）
            angle1 = offset + amplitude * math.sin(2 * math.pi * frequency * elapsed_time)

            # サーボ2の角度計算（位相π/2 = 90度ずらし）
            angle2 = offset + amplitude * math.sin(2 * math.pi * frequency * elapsed_time + math.pi / 2)

            # サーボ3の角度計算（位相π = 180度ずらし）
            angle3 = offset + amplitude * math.sin(2 * math.pi * frequency * elapsed_time + math.pi)

            # 角度を設定
            multi_servo.move_angle([angle1, angle2, angle3])

            time.sleep(0.02) # 20msごとに更新する

    except KeyboardInterrupt:
        print("デモを中断する。")
    finally:
        # サーボを停止する（電源を切るか、特定の位置に戻すなど）
        # サーボを0度の位置に戻す
        print("サーボを初期位置に戻す。")
        multi_servo.move_angle([0, 0, 0])
        time.sleep(1) # 角度が設定されるのを待つ
        multi_servo.off() # サーボのPWM信号を停止する
        pi.stop() # pigpioリソースを解放する

if __name__ == "__main__":
    synchronized_servo_dance()
