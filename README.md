# piservo0

`piservo0` は、Raspberry Piでサーボモーターを精密に制御するためのPythonライブラリです。
`pigpio`ライブラリを基盤とし、特にサーボモーターごとの個体差を吸収するためのキャリブレーション機能に重点を置いています。

## 特徴

- **シンプルなAPI**: 簡単なメソッド呼び出しでサーボモーターを直感的に操作できます。
- **パルス幅直接制御**: 角度ではなく、マイクロ秒単位のパルス幅を直接指定して、きめ細やかな制御が可能です。
- **キャリブレーション機能 (`CalibrableServo`)**:
    - サーボモーターごとの物理的な動作範囲（最小・中央・最大位置）をJSONファイルに保存し、個体差に応じた最適化ができます。
    - `set_min()`, `set_center()`, `set_max()` メソッドで、現在のサーボ位置を基準に簡単にキャリブレーションを行えます。
- **角度指定制御**: キャリブレーション後は、`-90`度から`+90`度の範囲で角度を指定してサーボを操作できます。
- **コマンドラインツール**: `uv run piservo0` コマンドを使って、ターミナルから直接サーボの動作確認やキャリブレーションが可能です。

## 準備

### `uv` のインストール
`uv` はPythonのパッケージ管理と仮想環境管理を高速に行うツールです。
以下のコマンドでインストールできます。
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

次に、仮想環境を作成し、依存関係をインストールします。

```bash
# 仮想環境の作成
uv venv

# 依存関係のインストール
uv pip install -e .
```

## 使い方

このライブラリは、`pigpio`デーモンが動作している必要があります。
まず、`pigpio`をインストールし、デーモンを起動してください。

```bash
# pigpioのインストール (Raspberry Pi OSにはプリインストールされていることが多いです)
sudo apt-get update
sudo apt-get install pigpio

# pigpioデーモンの起動
sudo systemctl start pigpiod
```

### 基本的な使い方 (`CalibrableServo`)

`CalibrableServo` を使うと、サーボモーターの個体差に合わせたキャリブレーションが簡単に行えます。

`samples/sample.py`
```python
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
    # --- キャリブレーションされた位置へ移動 ---
    print("Move to calibrated positions")
    servo.move_center()
    time.sleep(1)
    servo.move_min()
    time.sleep(1)
    servo.move_max()
    time.sleep(1)

    # --- 角度を指定して移動 ---
    print("Move by angle")
    servo.move_angle(-90)
    time.sleep(1)
    servo.move_angle(0)
    time.sleep(1)
    servo.move_angle(90)
    time.sleep(1)

finally:
    # サーボの電源をオフにする
    servo.off()
    pi.stop()

```

実行するには、`uv run` を使用します。

```bash
uv run python samples/sample.py
```

### コマンドラインからの操作

`piservo0` は、コマンドラインから直接サーボを操作する機能も提供します。
`uv run` を使って、以下のように実行できます。

**書式:**
```bash
# パルス幅を指定して移動
uv run piservo0 servo <PIN> <PULSE>

# キャリブレーション位置へ移動
uv run piservo0 servo <PIN> [min|center|max]

# 角度を指定して移動
uv run piservo0 servo <PIN> <ANGLE>deg

# 現在の位置をキャ��ブレーション値として設定
uv run piservo0 servo <PIN> [set_min|set_center|set_max]
```

**実行例:**

- GPIO 18番のサーボをパルス幅1500に動かす:
  ```bash
  uv run piservo0 servo 18 1500
  ```
- GPIO 18番のサーボをキャリブレーションされた中央位置に動かす:
  ```bash
  uv run piservo0 servo 18 center
  ```
- GPIO 18番のサーボを30度の位置に動かす:
  ```bash
  uv run piservo0 servo 18 30deg
  ```
- 現在のサーボ位置をGPIO 18番の最大値として設定する:
  ```bash
  uv run piservo0 servo 18 set_max
  ```
- ヘルプを表示する:
  ```bash
  uv run piservo0 --help
  ```

## 使用するピンについて

### 1. コマンドで確認
```
pinout
```

### 2. 公式サイト情報
[Raspberry Pi Pinout](pinout.xyz)

## APIリファレンス

より詳しいクラスやメソッドの仕様については、[`docs/REFERENCE.md`](docs/REFERENCE.md) をご覧ください。

## 依存ライブラリ

- [pigpio](https://abyz.me.uk/rpi/pigpio/)
- [click](https://pypi.org/project/click/)

## ライセンス

このプロジェクトはMITライセンスです。詳細は [`LICENSE`](LICENSE) ファイルをご覧ください。