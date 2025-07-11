# piservo0

`piservo0` は、Raspberry Piでサーボモーターを制御するためのシンプルなPythonライブラリです。
`pigpio`ライブラリを利用して、GPIOピン経由でサーボモーターのパルス幅を直接コントロールします。

## 特徴

- シンプルなAPIで簡単にサーボモーターを操作
- 角度ではなく、パルス幅を直接指定して制御
- 複数のサーボモーターを独立して管理可能

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

その後、サンプルコードを実行します。

`samples/sample.py`
```python
import time
from piservo0 import PiServo

# GPIO 18番ピンに接続されたサーボを操作する
servo = PiServo(18, debug=True)

try:
    # 中央位置に移動
    servo.move(PiServo.CENTER)
    time.sleep(1)

    # 最小位置に移動
    servo.move(PiServo.MIN)
    time.sleep(1)

    # 最大位置に移動
    servo.move(PiServo.MAX)
    time.sleep(1)

    # 中央位置に移動
    servo.move(PiServo.CENTER)
    time.sleep(1)

finally:
    # サーボの電源をオフにする
    servo.off()
```

実行するには、`uv run` を使用します。

```bash
uv run python samples/sample.py
```

## 使用するピンについて

### 1. コマンドで確認
```
pinout
```

### 2. 公式サイト情報
[Raspberry Pi Pinout](pinout.xyz)

## 詳細

より詳しいクラスの仕様については、[`REFERENCE.md`](REFERENCE.md) をご覧ください。

## 依存ライブラリ

- [pigpio](https://abyz.me.uk/rpi/pigpio/)
- [click](https://pypi.org/project/click/)

## ライセンス

このプロジェクトはMITライセンスです。詳細は [`LICENSE`](LICENSE) ファイルをご覧ください。
