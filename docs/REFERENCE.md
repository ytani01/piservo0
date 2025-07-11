# `piservo0` API Reference

## `PiServo` クラス

Raspberry PiのGPIOピンを介してサーボモーターを制御します。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `OFF` | `0` | サーボをオフにするためのパルス幅 |
| `MIN` | `500` | サーボの最小位置に対応するパルス幅 (マイクロ秒) |
| `MAX` | `2400` | サーボの最大位置に対応するパルス幅 (マイクロ秒) |
| `CENTER`| `1450`| サーボの中央位置に対応するパルス幅 (マイクロ秒) |

### `__init__(self, pi, pin, debug=False)`

`PiServo` オブジェクトを初期化します。

- **引数:**
    - `pi` (`pigpio.pi`): `pigpio.pi` のインスタンス。
    - `pin` (`int`): サーボが接続されているGPIOピン番号。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。デフォルトは `False`。

### `move(self, pulse)`

サーボモーターを指定されたパルス幅に移動させます。
パルス幅が `MIN` と `MAX` の範囲外の場合は、自動的に範囲内に調整されます。

- **引数:**
    - `pulse` (`int`): 設定するパルス幅 (マイクロ秒)。

### `min(self)`

サーボモーターを最小位置に移動させます。パルス幅を `MIN` に設定します。

### `max(self)`

サーボモーターを最大位置に移動させます。パルス幅を `MAX` に設定します。

### `center(self)`

サーボモーターを中央位置に移動させます。パルス幅を `CENTER` に設定します。

### `off(self)`

サーボモーターの電源をオフにします。パルス幅を `0` に設定して動作を停止させます。
