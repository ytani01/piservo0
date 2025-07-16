import time
import pigpio
from piservo0.multi_servo import MultiServo

def synchronized_pose_demo():
    """
    3つのサーボモーターが同期して複数のポーズを順番に取るデモプログラムである。
    move_angle_sync()を使用して滑らかな動きを実現する。
    """
    print("シンクロナイズド・ポーズ・シーケンスを開始する。")

    # サーボ設定ファイルのパス
    config_file = "samples/sample_servo.json" # samplesディレクトリのファイルを使う

    # pigpioデーモンに接続する
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioデーモンに接続できない。実行前に 'sudo pigpiod' を実行する。")
        return

    # サーボのピン番号を固定する
    servo_pins = [18, 21, 24]

    # MultiServoを初期化する
    # CalibrableServoが設定ファイルを読み込むため、ここでconf_fileを渡す
    multi_servo = MultiServo(pi, servo_pins, conf_file=config_file)

    # ポーズの定義: [サーボ1の角度, サーボ2の角度, サーボ3の角度]
    poses = [
        [0, 0, 0],      # 全て中央
        [90, -90, 0],   # サーボ1:右, サーボ2:左, サーボ3:中央
        [-90, 90, 0],   # サーボ1:左, サーボ2:右, サーボ3:中央
        [0, 0, 90],     # サーボ1:中央, サーボ2:中央, サーボ3:右
        [0, 0, -90],    # サーボ1:中央, サーボ2:中央, サーボ3:左
        [45, 45, 45],   # 全て右斜め
        [-45, -45, -45]  # 全て左斜め
    ]

    # 各ポーズへの移動時間（秒）
    move_duration = 1.0
    # 各ポーズでの待機時間（秒）
    wait_duration = 0.5

    try:
        print("ポーズシーケンスを開始する。")
        while True:
            for i, pose in enumerate(poses):
                print(f"ポーズ {i+1}/{len(poses)}: {pose} へ移動する。")
                multi_servo.move_angle_sync(pose, estimated_sec=move_duration)
                time.sleep(wait_duration)

    except KeyboardInterrupt:
        print("デモを中断する。")
    finally:
        # サーボを停止する
        # サーボを0度の位置に戻す
        print("サーボを初期位置に戻す。")
        multi_servo.move_angle([0, 0, 0])
        time.sleep(1) # 角度が設定されるのを待つ
        multi_servo.off() # サーボのPWM信号を停止する
        pi.stop() # pigpioリソースを解放する

if __name__ == "__main__":
    synchronized_pose_demo()
