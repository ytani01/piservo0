# piservo0: 

`piservo0` は、Raspberry Piでサーボモーターを精密に制御するためのPythonライブラリです。
`pigpio`ライブラリを基盤とし、安価なサーボモーター(SG90など)を複数、同期させて動かすことに重点を置き、サーボモーターごとの個体差を吸収するためのキャリブレーション機能もあります。


## == 特徴

### --- `pigpio`をベースにしているので…

- 追加のハードウェア(PCA9685など)は不要です。Raspberry PiのGPIOで、直接サーボを制御できます。
- ほぼすべてのGPIOをサーボ制御用として使えます。(PWM用のピンを選ぶ必要はありません。)
- ハードウェアPWMと遜色のない性能が出せます。Raspberry Pi Zeroでも、4個以上のサーボを問題なく同時に動かせます。


### --- さらに、本ライブラリでは…

- **複数のサーボを同期**させながら動かすことができます。ロボットの制御に最適です。
- **キャリブレーション(補正)機能**があり、-90度、 0度、+90度の位置を補正でき、ファイルに補正値を保存します。安価なサーボをより実用的に利用できます。
- キャリブレーションのためのツールも含まれてます。
- **ネットワーク経由**で、**`REST API`**で制御することもできます。
- 入門用や、簡単にサーボを動かせる、より**シンプルなAPIも**用意してます。


## == インストール

ライブラリを利用するだけであれば、こちらの方法でインストールしてください。

※ Raspbery Pi OS のインストールと、一般的な設定については省略してます。


**1. `pigpio`のインストールと起動**

このライブラリは、`pigpio`デーモンが動作している必要があります。
まず、`pigpio`をインストールし、デーモンを起動してください。

```bash
# pigpioのインストール (Raspberry Pi OSにはプリインストールされていることが多いです)
sudo apt install pigpio

# pigpioデーモンの起動
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

**2. 開発環境の設定 -- `mise`と`uv`のインストール**

`mise` は、プロジェクトごとにPythonのバージョンなどを管理するツールです。
`uv` は、高速なPythonパッケージ管理ツールです。

```bash
# miseのインストール
curl https://mise.run | sh
# PATHを通す
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
# (ターミナルを再起動)

# mise経由でuvをインストール
mise use --global uv@latest
```

**3. リポジトリのクローンとセットアップ**

```bash
# 任意の作業ディレクトリを作成
mkdir -p ~/work
cd ~/work

# リポジトリをクローン
git clone https://github.com/ytani01/piservo0.git
cd piservo0

# 仮想環境の作成と有効化
uv venv
source .venv/bin/activate

# 依存関係のインストール
uv pip install -e .        # 実行用
uv pip install -e '.[dev]' # 開発用
```


## == 使い方

このライブラリは、単純なものから複雑なものまで、段階的に使えるように設計されています。

### --- 1. 基本的な使い方 (`PiServo`)

まず、1つのサーボモーターを直接制御する例です。
`PiServo`クラスは、指定したGPIOピンに接続されたサーボを、パルス幅で制御する最も基本的な機能を提供します。

```python
# samples/sample_01_piservo.py
import time
import pigpio
from piservo0 import PiServo

PIN = 18

pi = pigpio.pi()
if not pi.connected:
    print("pigpio not connected.")
    exit()

servo = PiServo(pi, PIN)

try:
    print("Move to center")
    servo.move_center()
    time.sleep(1)

    print("Move to min")
    servo.move_min()
    time.sleep(1)

    print("Move to max")
    servo.move_max()
    time.sleep(1)

finally:
    print("Turning off")
    servo.off()
    pi.stop()
```

### --- 2. キャリブレーション機能を使う (`CalibrableServo`)

安価なサーボモーターは、製品の個体差により、同じパルス幅でも回転角度が微妙に異なります。
`CalibrableServo`クラスを使うと、各サーボの最小(-90度)、中央(0度)、最大(+90度)の位置を調整し、その設定を `servo.json` ファイルに保存できます。

これにより、より正確な角度での制御が可能になります。

```python
# samples/sample_02_calibrable_servo.py
import time
import pigpio
from piservo0 import CalibrableServo

PIN = 18

pi = pigpio.pi()
if not pi.connected:
    print("pigpio not connected.")
    exit()

# CalibrableServoはキャリブレーション値をファイルから読み込みます
servo = CalibrableServo(pi, PIN)

try:
    # -90度から90度の範囲で角度を指定して動かす
    for angle in [-90, -45, 0, 45, 90, 0]:
        print(f"Move to {angle} deg")
        servo.move_angle(angle)
        time.sleep(1)

finally:
    print("Turning off")
    servo.off()
    pi.stop()
```

### --- 3. 複数のサーボを動かす (`MultiServo`)

`MultiServo`クラスは、複数の`CalibrableServo`をまとめて扱います。
ロボットアームのように、複数のサーボを同時に、しかしそれぞれ異なる角度に動かしたい場合に便利です。

```python
# samples/sample_03_multi_servo.py
import time
import pigpio
from piservo0 import MultiServo

PINS = [18, 23]

pi = pigpio.pi()
if not pi.connected:
    print("pigpio not connected.")
    exit()

# 2つのサーボをMultiServoで管理
multi_servo = MultiServo(pi, PINS)

try:
    # 各サーボを異なる角度に動かす
    print("Move to [90, -90]")
    multi_servo.move_angle([90, -90])
    time.sleep(1)

    print("Move to [0, 0]")
    multi_servo.move_angle([0, 0])
    time.sleep(1)

    # 1番目のサーボだけ動かす (Noneを指定すると現在の角度を維持)
    print("Move to [-90, None]")
    multi_servo.move_angle([-90, None])
    time.sleep(1)

finally:
    print("Turning off")
    multi_servo.off()
    pi.stop()
```

### --- 4. 複数のサーボを滑らかに同期させて動かす (`MultiServo.move_angle_sync`)

`MultiServo`の`move_angle_sync`メソッドを使うと、複数のサーボがそれぞれの目標角度まで、指定した時間をかけて同時に到着するように、滑らかに動かすことができます。これにより、ロボットのダンスのような、より自然で協調した動きが実現できます。

```python
# samples/sample_04_synchronized_servo_dance.py
import time
import pigpio
from piservo0 import MultiServo

PINS = [18, 23, 24, 25]

pi = pigpio.pi()
if not pi.connected:
    print("pigpio not connected.")
    exit()

dance_bot = MultiServo(pi, PINS)

# ダンスの振り付け
dance_moves = [
    {"angles": [90, -90, 90, -90], "time": 1.0},
    {"angles": [-90, 90, -90, 90], "time": 1.0},
    {"angles": [45, -45, 45, -45], "time": 0.5},
    {"angles": [-45, 45, -45, 45], "time": 0.5},
    {"angles": [0, 0, 0, 0], "time": 1.0},
]

try:
    print("Start Dance!")
    for move in dance_moves:
        print(f"Moving to {move['angles']} in {move['time']}s")
        dance_bot.move_angle_sync(move["angles"], move_sec=move["time"])
    print("Finish!")

finally:
    print("Turning off")
    dance_bot.off()
    pi.stop()
```

### --- 5. 応用的な使い方: 非同期制御 (`ThreadMultiServo`)

`ThreadMultiServo` は、バックグラウンドスレッドでサーボモーターを制御するため、メインプログラムの実行をブロックせずに複数のサーボを同期して動かすことができます。これにより、より複雑なロボットの動作や、リアルタイム性が求められるアプリケーションに適しています。

```python
# ``ThreadMultiServo``の例
import time
import pigpio
from piservo0 import ThreadMultiServo

PIN = [18, 21]

pi = pigpio.pi()

# ThreadMultiServoのインスタンスを作成
# バックグラウンドスレッドが自動的に開始される
servo = ThreadMultiServo(pi, PIN)

# コマンドをキューに追加し、バックグラウンドで実行
servo.send_cmd({"cmd": "move_angle_sync", "target_angles": [90, -90]})
time.sleep(1) # コマンドが実行されるのを待つ

servo.send_cmd({"cmd": "move_angle_sync", "target_angles": [0, 0]})
time.sleep(1) # コマンドが実行されるのを待つ

# 終了処理
servo.end()
pi.stop()
```

**実行方法:**

```bash
# 仮想環境が有効化されていることを確認
# source .venv/bin/activate

# サンプルコードを実行
python samples/sample_01_piservo.py
```

## == コマンド体系

本ライブラリでは、動作を指示するために「JSONコマンド」と「短縮文字列コマンド」の2種類の書式が利用されます。

### --- JSONコマンド

`ThreadMultiServo` や `Web JSON API` で使用される、より詳細な制御が可能なコマンド形式です。

- **書式**: `{"cmd": "コマンド名", "パラメータ名": 値, ...}`
- **例**: 
  - `{"cmd": "move_angle_sync", "target_angles": [40, 30, null, 10]}`
    - 複数のサーボを同期して指定角度に移動（`null`は現在の角度を維持）
  - `{"cmd": "sleep", "sec": 1.5}`
    - 1.5秒待機
  - `{"cmd": "move_sec", "sec": 0.5}`
    - `move_angle_sync` のデフォルト動作時間を0.5秒に設定

より詳細なコマンド一覧は [`docs/JSON_CMD.md`](docs/JSON_CMD.md) をご覧ください。

### --- 短縮文字列コマンド

`Web String API` などで、より手軽にコマンドを送信するための簡易的な形式です。内部でJSONコマンドに変換されます。

- **書式**: `コマンド種別:パラメータ`
- **例**: 
  - `mv:40,30,.,10` -> 4つのサーボをそれぞれ 40度, 30度, 現在位置, 10度 に動かす
  - `sl:1.5` -> 1.5秒待機
  - `ms:0.5` -> デフォルトの動作時間を0.5秒に設定
  - `ca` -> コマンドキューをキャンセル

より詳細なコマンド一覧は [`docs/STR_CMD.md`](docs/STR_CMD.md) をご覧ください。


## == CLI / Web API

### --- コマンドラインからの操作

`piservo0` は、コマンドラインから直接サーボを操作する機能も提供します。

**書式:**
```bash
# 仮想環境が有効化されていることを確認
# source .venv/bin/activate

# 単一のサーボモーターをパルスで制御
piservo0 servo --help
piservo0 servo 18 1500

# サーボ‐モーターのキャリブレーション 
piservo0 cservo --help
piservo0 cservo 18

# 複数サーボの同時操作
piservo0 multi --help
piservo0 multi 18 21
```

### --- Web API

Web APIを使えば、HTTP経由でリモートから制御することができます。

◆◆ **`Web String API`** ◆◆

ブラウザのアドレスバーや`curl`から、手軽に複数のサーボを制御できます。

**サーバーの起動:**
```bash
uv run piservo0 web-str-api --pins 18,23,24,25
```

**クライアントからの操作例:**
```bash
# 4つのサーボを 90, -90, 90, -90 度に動かし、1秒待機
curl http://<RaspberryPiのIP>:8000/cmd/mv:90,-90,90,-90%20sl:1

# 中央位置に戻す
curl http://<RaspberryPiのIP>:8000/cmd/mv:0,0,0,0
```
詳細は[`docs/WEB_API.md`](docs/WEB_API.md) をご覧ください。


◆◆ **`Web JSON API`** ◆◆

JSON形式で、より複雑なコマンドシーケンスを送信できます。

**サーバーの起動:**
```bash
uv run piservo0 web-json-api 18 23 24 25
```

**クライアントからの操作例:**
```bash
# 複数のコマンドをJSON配列で一度に送信
curl -X POST -H "Content-Type: application/json" \
-d \
'[
    {"cmd": "move_angle_sync", "target_angles": [90, -90, 90, -90], "move_sec": 1.0},
    {"cmd": "sleep", "sec": 0.5},
    {"cmd": "move_angle_sync", "target_angles": [0, 0, 0, 0], "move_sec": 1.0}
]' \
http://<RaspberryPiのIP>:8000/cmd
```

## == 使用するGPIOピンについて

ほとんどのGPIOピンを使うことができます。

### --- 1. コマンドで確認
```
pinout
```

```
   3V3  (1) (2)  5V    
 GPIO2  (3) (4)  5V    
 GPIO3  (5) (6)  GND   
 GPIO4  (7) (8)  GPIO14
   GND  (9) (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND   
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND   
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8 
   GND (25) (26) GPIO7 
 GPIO0 (27) (28) GPIO1 
 GPIO5 (29) (30) GND   
 GPIO6 (31) (32) GPIO12
GPIO13 (33) (34) GND   
GPIO19 (35) (36) GPIO16
GPIO26 (37) (38) GPIO20
   GND (39) (40) GPIO21
```

### --- 2. 公式サイト情報
[Raspberry Pi Pinout](https://pinout.xyz/)


## ソフトウェア内部情報

### === ソフトウェア・アーキテクチャ

![Architecture](docs/SoftwareArchitecture.png)


### === APIリファレンス ===

より詳しいクラスやメソッドの仕様については、以下のコマンドを実行してください。

```bash
uv run python -m pydoc piservo0
```

### === 他のプロジェクトから依存ライブラリとして、本プロジェクトを参照する場合の例 ===

`pyproject.toml`
```
:
dependencies = [
    "piservo0",
]
:
[tool.uv.sources]
piservo0 = { path = "../piservo0" }
:
```

## == 依存ライブラリ

- [pigpio](https://abyz.me.uk/rpi/pigpio/)
- [click](https://pypi.org/project/click/)

## == ライセンス

このプロジェクトはMITライセンスです。詳細は [`LICENSE`](LICENSE) ファイルをご覧ください。

```