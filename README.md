# piservo0: 

`piservo0` は、Raspberry Piでサーボモーターを精密に制御するためのPythonライブラリです。
`pigpio`ライブラリを基盤とし、特にサーボモーターごとの個体差を吸収するためのキャリブレーション機能に重点を置いています。

## == 特徴

- **シンプルなAPI**: 簡単なメソッド呼び出しでサーボモーターを直感的に操作できます。
- **キャリブレーション機能 (`CalibrableServo`)**:
    - サーボモーターごとの物理的な動作範囲（最小・中央・最大位置）をJSONファイルに保存し、個体差に応じた最適化ができます。
    - `set_min()`, `set_center()`, `set_max()` メソッドで、現在のサーボ位置を基準に簡単にキャリブレーションを行えます。
- **複数サーボモーターの制御**: 複数のサーボモーターを同時にタイミングをあわせて動かすことができます。
- **角度指定制御**: キャリブレーション後は、`-90`度から`+90`度の範囲で角度を指定してサーボを操作できます。
- **パルス幅直接制御**: 角度ではなく、マイクロ秒単位のパルス幅を直接指定して、きめ細やかな制御が可能です。
- **コマンドラインツール**: ターミナルから直接サーボの動作確認やキャリブレーションが可能です。

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
uv pip install -e .        # 実行用
uv pip install -e '.[dev]' # 開発用
```

## == 使い方

### --- 基本的な使い方 (`CalibrableServo`)

`CalibrableServo` を使うと、サーボモーターの個体差に合わせたキャリブレーションが簡単に行えます。

`MultiServo` を使うと、複数サーボモーターを同時に動かすことができます。

[`samples/`](samples/) をご覧ください。

```python
# ``CalibrableServo``の例

import time
import pigpio
from piservo0 import CalibrableServo

PIN = 18

pi = pigpio.pi()

servo = CalibrableServo(pi, PIN)

servo.move_angle(-45)
time.sleep(1)
servo.move_max()
time.sleep(1)
servo.move_center()
time.sleep(1)

servo.off()
pi.stop()
```

```python
# ``MultiServo``の例

import time
import pigpio
from piservo0 import MultiServo

PIN = [18, 21]

pi = pigpio.pi()

servo = MultiServo(pi, PIN)

servo.move_angle_sync([90, -90])
servo.move_angle_sync([0, 0])

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

### --- コマンドラインからの操作

`piservo0` は、コマンドラインから直接サーボを操作する機能も提供します。

**書式: (仮想環境で使う場合) **
```bash
source venv/bin/activate

# 単一のサーボモーターをプルスで制御
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
[Raspberry Pi Pinout](pinout.xyz)

## == APIリファレンス

より詳しいクラスやメソッドの仕様については、[`docs/REFERENCE.md`](docs/REFERENCE.md) をご覧ください。

## == 依存ライブラリ

- [pigpio](https://abyz.me.uk/rpi/pigpio/)
- [click](https://pypi.org/project/click/)

## == ライセンス

このプロジェクトはMITライセンスです。詳細は [`LICENSE`](LICENSE) ファイルをご覧ください。
