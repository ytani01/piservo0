# samples/sample_06_calibration_tool.py

import time
import blessed
import click
import pigpio
import json

from piservo0.calibrable_servo import CalibrableServo

# デフォルトの設定ファイルパス
DEFAULT_CONFIG_FILE = "sample_servo.json"

def print_status(servo):
    """現在のサーボの状態を新しい行に出力する"""
    angle = servo.get_angle()
    pulse = servo.get_pulse()
    min_p = servo.min
    center_p = servo.center
    max_p = servo.max
    
    status_line = (
        f"Angle={angle:>5.1f}, Pulse={pulse:>4d} | "
        f"Min={min_p:>4d}, Center={center_p:>4d}, Max={max_p:>4d}"
    )
    print(status_line)

@click.command()
@click.option('--config-file', '-c', default=DEFAULT_CONFIG_FILE,
              help=f"サーボ設定ファイルのパス (デフォルト: {DEFAULT_CONFIG_FILE})")
@click.option('--pin', '-p', type=int,
              help="GPIOピン番号 (設定ファイルより優先)")
def main(config_file, pin):
    """
    サーボモーターのキャリブレーションを対話的に行うCLIツール。
    """
    term = blessed.Terminal()

    # pigpioの初期化
    pi = pigpio.pi()
    if not pi.connected:
        print(term.red("pigpioに接続できませんでした。pigpiodが実行されているか確認してください。"))
        return

    # ピン番号の解決
    servo_pin = pin
    if servo_pin is None:
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                first_servo_key = list(config_data.keys())[0]
                servo_pin = config_data[first_servo_key].get('pin')
                if servo_pin is None:
                    raise ValueError("設定ファイルに 'pin' が見つかりません。")
        except (FileNotFoundError, IndexError, json.JSONDecodeError, ValueError) as e:
            print(term.red(f"\n設定ファイル '{config_file}' からピン番号を読み込めませんでした。"))
            print(term.red(f"エラー: {e}"))
            print(term.yellow("-p オプションでピン番号を直接指定してください。例: -p 18"))
            pi.stop()
            return
    
    # サーボを初期化
    try:
        servo = CalibrableServo(pi, servo_pin, conf_file=config_file)
    except Exception as e:
        print(term.red(f"\nサーボの初期化に失敗しました: {e}"))
        pi.stop()
        return

    # 操作方法を表示
    print("\nサーボキャリブレーションツール")
    print("-" * 40)
    print(f" GPIOピン: {servo_pin}, 設定ファイル: {config_file}")
    print(" [←]/[→]: 角度調整")
    print(" [c]: 現在位置を[中央]に設定")
    print(" [[]: 現在位置を[最小]に設定")
    print(" []]: 現在位置を[最大]に設定")
    print(" [s]: 設定をファイルに保存")
    print(" [q]: 終了")
    print("-" * 40)

    # 初期位置に移動し、状態を表示
    servo.move_center()
    print_status(servo)

    with term.cbreak():
        val = ''
        while val.lower() != 'q':
            val = term.inkey()
            if not val:
                continue

            action = True
            if val.code == term.KEY_LEFT:
                current_angle = servo.get_angle()
                servo.move_angle(max(servo.ANGLE_MIN, current_angle - 1))
            elif val.code == term.KEY_RIGHT:
                current_angle = servo.get_angle()
                servo.move_angle(min(servo.ANGLE_MAX, current_angle + 1))
            elif val.lower() == 'c':
                servo.set_center()
            elif val.lower() == '[':
                servo.set_min()
            elif val.lower() == ']':
                servo.set_max()
            elif val.lower() == 's':
                servo.save_conf()
                print(f"--- 設定を {config_file} に保存しました。 ---")
            else:
                action = False

            if action:
                print_status(servo)

    print("\nキャリブレーションツールを終了します。")
    servo.release()
    pi.stop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
