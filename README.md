# piservo0: 

`piservo0` は、Raspberry Piでサーボモーターを精密に制御するためのPythonライブラリです。
`pigpio`ライブラリを基盤とし、安価なサーボモーター(SG90など)を複数、同期させて動かすことに重点を置き、サーボモーターごとの個体差を吸収するためのキャリブレーション機能もあります。

## == 特徴

### --- `pigpio`をベースにしているので…

- 追加のハードウェア(PCA9685など)は不要です。Raspberry PiのGPIOで、直接サーボを制御できます。
- ほぼすべてのGPIOをサーボ制御用として使えます。(PWM用のピンを選ぶ必要はありません。)
- ハードウェアPWMと遜色のない性能が出せます。Raspberry Pi Zeroでも、4個以上のサーボを問題なく同時に動かせます。

### --- さらに、本ライブラリでは…

- 複数のサーボを同期させながら動かすことができます。ロボットの制御に最適です。
- キャリブレーション(補正)機能があり、-90度、 0度、+90度の位置を補正でき、ファイルに補正値を保存します。安価なサーボをより実用的に利用できます。
- キャリブレーションのためのツールも含まれてます。
- シンプルなAPIで、簡単なメソッド呼び出しで、サーボモーターを直感的に操作できます。(「デューティー比」とか専門知識は不要です。)
- 角度指定と、パルス指定の両方のAPIを用意してます。
- 入門用や、簡単にサーボを動かしたい場合のために、キャリブレーションや複数サーボの動機は不要のシンプルなAPIも用意してます。


## == インストール

### --- 通常の利用者向け (推奨)

ライブラリを利用するだけであれば、こちらの方法でインストールしてください。

**1. `pigpio`のインストールと起動**

このライブラリは、`pigpio`デーモンが動作している必要があります。
まず、`pigpio`をインストールし、デーモンを起動してください。

```bash
# pigpioのインストール (Raspberry Pi OSにはプリインストールされていることが多いです)
sudo apt-get update
sudo apt-get install pigpio

# pigpioデーモンの起動
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

**2. ライブラリのダウンロードとインストール**

次に、`piservo0`ライブラリをインストールします。

- **ダウンロード**: [Releases](https://github.com/ytani01/piservo0/releases) ページから、最新の `.whl` ファイルをダウンロードします。

- **インストール**: ダウンロードしたファイルを`pip`でインストールします。仮想環境の利用を強く推奨します。

  ```bash
  # 仮想環境を作成し、有効化する
  python3 -m venv .venv
  source .venv/bin/activate

  # pipでwhlファイルをインストール
  pip install /path/to/piservo0-x.x.x-py3-none-any.whl
  ```
  ※ `/path/to/` の部分は、ダウンロードしたファイルの実際のパスに置き換えてください。

### --- 開発者向け

ソースコードを編集したり、開発に貢献したりする場合は、以下の手順でセットアップしてください。

**1. `uv` のインストール**

`uv` は高速なPythonパッケージインストーラー兼リゾルバーです。
以下のコマンドでインストールできます。
```bash
# uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# uv へのPATHを通す
# ~/.bashrcなどに書いておくことが望ましい。
export PATH=$PATH:~/.local/bin
```

**2. リポジトリのクローンとセットアップ**

```bash
mkdir work1

# リポジトリをクローン
git clone https://github.com/ytani01/piservo0.git
cd piservo0

# 仮想環境の作成
uv venv

# 依存関係のインストール
uv pip install -e .        # 実行用
uv pip install -e '.[dev]' # 開発用
```

## == 使い方

### --- 基本的な使い方 (`ThreadMultiServo`)

`ThreadMultiServo` は、バックグラウンドスレッドでサーボモーターを制御するため、メインプログラムの実行をブロックせずに複数のサーボを同期して動かすことができる。これにより、より複雑なロボットの動作や、リアルタイム性が求められるアプリケーションに適している。

`CalibrableServo` を使うと、サーボモーターの個体差に合わせたキャリブレーションが簡単に行える。`ThreadMultiServo` は内部で `CalibrableServo` を利用しているため、キャリブレーション機能も利用できる。

具体的な使用例は、[`samples/`](samples/) をご覧ください。

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

仮想環境を有効化している場合:
```bash
python samples/sample.py
```

`uv` を使用する場合:
```bash
uv run python samples/sample.py
```

### --- コマンドラインからの操作

`piservo0` は、コマンドラインから直接サーボを操作する機能も提供します。

**書式: (仮想環境で使う場合) **
```bash
source venv/bin/activate

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

**書式: (uvを使う場合) **
```bash
uv run piservo0 servo --help
uv run piservo0 servo 18 1500

uv run piservo0 cservo --help
uv run piservo0 cservo 18

文字列コマンドによるサーボ制御については、[`STR_CMD.md`](docs/STR_CMD.md) をご覧ください。
```

### --- Web API

Web APIによるサーボ制御については、[`WEB_API.md`](docs/WEB_API.md) をご覧ください。


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

## == APIリファレンス

より詳しいクラスやメソッドの仕様については、以下のコマンドを実行してください。

```bash
uv run python -m pydoc piservo0
```

### --- 他のプロジェクトから依存ライブラリとして、本プロジェクトを参照する場合の例

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
