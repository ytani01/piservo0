# piservo0: 

`piservo0` は、Raspberry Piでサーボモーターを精密に制御するためのPythonライブラリです。
`pigpio`ライブラリを基盤とし、特にサーボモーターごとの個体差を吸収するためのキャリブレーション機能に重点を置いています。

## 特徴

- **シンプルなAPI**: 簡単なメソッド呼び出しでサーボモーターを直感的に操作できます。
- **パルス幅直接制御**: 角度ではなく、マイクロ秒単位のパルス幅を直接指定して、きめ細やかな制御が可能です。
- **キャリブレーション機能 (`CalibrableServo`)**:
    - サーボモーターごとの物理的な動作範囲（最小・中央・最大位置）をJSONファイルに保存し、個体差に応じた最適化ができます。
    - `set_min()`, `set_center()`, `set_max()` メソッドで、現在のサーボ位置を基準に簡単にキャリブレーションを行えます。
- **角度指定制御**: キャリブレーション後は、`-90`度から`+90`度の範囲で角度を指定してサーボを操作できます。
- **コマンドラインツール**: ターミナルから直接サーボの動作確認やキャリブレー���ョンが可能です。

## インストール

### 通常の利用者向け (推奨)

ライブラリを利用するだけであれば、こちらの方法でインストールしてください。

**1. `pigpio`のインストールと起動**

このライブラリは、`pigpio`デーモンが動作している必要があります。
まず、`pigpio`をインストールし、デーモンを起動してください。

```bash
# pigpioのインストール (Raspberry Pi OSにはプリインストールされていることが多いです)
sudo apt-get update
sudo apt-get install pigpio

# pigpioデーモンの起動
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
  ��� `/path/to/` の部分は、ダウンロードしたファイルの実際のパスに置き換えてください。

### 開発者向け

ソースコードを編集したり、開発に貢献したりする場合は、以下の手順でセットアップしてください。

**1. `uv` のインストール**

`uv` は高速なPythonパッケージインストーラー兼リゾルバーです。
以下のコマンドでインストールできます。
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. リポジトリのクローンとセットアップ**

```bash
# リポジトリをクローン
git clone https://github.com/ytani01/piservo0.git
cd piservo0

# 仮想環境の作成
uv venv

# 依存関係のインストール
uv pip install -e .
```

## 使い方

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

**実行方法:**

仮想環境を有効化している場合:
```bash
python samples/sample.py
```

`uv` を使用する場合:
```bash
uv run python samples/sample.py
```

### コマンドラインからの操作

`piservo0` は、コマンドラインから直接サーボを操作する機能も提供します。

**書式:**
```bash
# (仮想環境を有効化した後)
piservo0 servo <PIN> <PULSE>
piservo0 servo <PIN> [min|center|max]
piservo0 servo <PIN> <ANGLE>deg
piservo0 servo <PIN> [set_min|set_center|set_max]
```

**実行例:**

- GPIO 18番のサーボをパルス幅1500に動かす:
  ```bash
  piservo0 servo 18 1500
  ```
- GPIO 18番のサーボをキャリブレーションされた中央位置に��かす:
  ```bash
  piservo0 servo 18 center
  ```
- GPIO 18番のサーボを30度の位置に動かす:
  ```bash
  piservo0 servo 18 30deg
  ```
- 現在のサーボ位置をGPIO 18番の最大値として設定する:
  ```bash
  piservo0 servo 18 set_max
  ```
- ヘルプを表示する:
  ```bash
  piservo0 --help
  ```

`uv` を使用する場合は、`piservo0` の前に `uv run` を付けます。
```bash
uv run piservo0 servo 18 1500
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