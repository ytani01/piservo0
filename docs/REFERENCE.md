# `piservo0` API Reference

## `MultiServo` クラス

複数のサーボモーター (`CalibrableServo`) を同時に制御するためのクラスです。

### `__init__(self, pi, pins, first_move=True, conf_file='./servo.json', debug=False)`

`MultiServo` オブジェクトを初期化します。
内部で `CalibrableServo` のインスタンスをピンの数だけ生成します。

- **引数:**
    - `pi` (`pigpio.pi`): `pigpio.pi` のインスタンス。
    - `pins` (`list[int]`): サーボが接続されているGPIOピン番号のリスト。
    - `first_move` (`bool`, optional): 初期化時にサーボを中央 (`0`度) に移動させるかどうかのフラグ。デフォルトは `True`。
    - `conf_file` (`str`, optional): 各サーボのキャリブレーション設定ファイルのパス。デフォルトは `./servo.json`。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。デフォルトは `False`。

### `off(self)`

すべてのサーボモーターの電源をオフにします。

### `get_pulse(self)`

すべてのサーボモーターの現在のパルス幅をリストで取得します。

- **戻り値:**
    - `list[int]`: 各サーボの現在のパルス幅のリスト (マイクロ秒)。

### `get_angle(self)`

すべてのサーボモーターの現在の角度をリストで取得します。

- **戻り値:**
    - `list[float]`: 各サーボの現在の角度のリスト。

### `move_angle(self, angle)`

各サーボモーターを、リストで指定されたそれぞれの角度に移動させます。

- **引数:**
    - `angle` (`list[float]`): 各サーボに設定する角度のリスト。リストの要素数は `pins` と一致している必要があります。

### `move_angle_sync(self, angle, estimated_sec=1.0, step_n=50)`

すべてのサーボモーターを、指定された角度まで同期的かつ滑らかに移動させます。
開始角度から目標角度までを `step_n` 回に分割して、少しずつ動かします。

- **引数:**
    - `angle` (`list[float]`): 各サーボの目標角度のリスト。
    - `estimated_sec` (`float`, optional): 移動にかかるおおよその時間 (秒)。デフォルトは `1.0`。
    - `step_n` (`int`, optional): 移動の分割ステップ数。数値を大きくすると、より滑らかに動きます。デフォルトは `50`。

---

## `CalibrableServo` クラス

`PiServo`を拡張し、JSONファイルによるキャリブレーション機能を追加したクラスです。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `ANGLE_MIN` | `-90.0` | 最小角度 |
| `ANGLE_MAX` | `90.0` | 最大角度 |
| `ANGLE_CENTER`| `0.0`| 中央角度 |

### `__init__(self, pi, pin, conf_file='./servo.json', debug=False)`

`CalibrableServo` オブジェクトを初期化します。
指定された `conf_file` を読み込み、ピン番号に対応するキャリブレーション値を適��します。ファイルが存在しない場合は、デフォルト値で新たに作成されます。

- **引数:**
    - `pi` (`pigpio.pi`): `pigpio.pi` のインスタンス。
    - `pin` (`int`): サーボが接続されているGPIOピン番号。
    - `conf_file` (`str`, optional): キャリブレーション設定ファイルのパス。デフォルトは `./servo.json`。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。デフォルトは `False`。

### インスタンス変数

- `center` (`int`): キャリブレーション後の中央位置のパルス幅。
- `min` (`int`): キャリブレーション後の最小位置のパルス幅。
- `max` (`int`): キャリブレーション後の最大位置のパルス幅。

### 移動メソッド

キャリブレーション値を考慮してサーボモ���ターを移動させます。

- `move_pulse(self, pulse)`: 指定したパルス幅へ移動します。パルス幅がキャリブレーション範囲外の場合は動作しません。
- `move_center(self)`: キャリブレーションされた中央位置へ移動します。
- `move_min(self)`: キャリブレーションされた最小位置へ移動します。
- `move_max(self)`: キャリブレーションされた最大位置へ移動します。
- `move_angle(self, deg)`: 指定された角度へ移動します。

### 角度・パルス幅変換メソッド

- `deg2pulse(self, deg)`: 角度をパルス幅に変換します。

### キャリブレーション設定メソッド

- `set_center(self, pulse=None)`: 中央位置のパルス幅を更新し、設定ファイルに保存します。引数を省略すると現在の値が使われます。
- `set_min(self, pulse=None)`: 最小位置のパルス幅を更新し、設定ファイルに保存します。引数を省略すると現在の値が使われます。
- `set_max(self, pulse=None)`: 最大位置のパルス幅を更新し、設定ファイルに保存します。引数を省略すると現在の値が使われます。

### 設定ファイル管理メソッド

- `load_conf(self, conf_file=None)`: 設定ファイルからキャリブレーション値を読��込みます。
- `save_conf(self, conf_file=None)`: 現在のキャリブレーション値を設定ファイルに保存します。
- `read_jsonfile(self, conf_file=None)`: 設定ファイルを読み込み、内容をリストとして返します。
- `nomalize_pulse1(self, pulse)`: パルス幅を `PiServo` の `MIN` と `MAX` の範囲に正規化します。

---

## `PiServo` クラス

Raspberry PiのGPIOピンを介してサーボモーターを制御します。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `OFF` | `0` | サーボをオフにするためのパルス幅 |
| `MIN` | `500` | サーボの最小位置に対応するデフォルトのパルス幅 (マイクロ秒) |
| `MAX` | `2400` | サーボの最大位置に対応するデフォルトのパルス幅 (マイクロ秒) |
| `CENTER`| `1450`| サーボの中央位置に対応するデフォルトのパルス幅 (マイクロ秒) |

### `__init__(self, pi, pin, debug=False)`

`PiServo` オブジェクトを初期化します。

- **引数:**
    - `pi` (`pigpio.pi`): `pigpio.pi` のインスタンス。
    - `pin` (`int`): サーボが接続されているGPIOピン番号。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。デフォルトは `False`。

### `move_pulse(self, pulse)`

サーボモ��ターを指定されたパルス幅に移動させます。
パルス幅が `MIN` と `MAX` の範囲外の場合は、自動的に範囲内に調整されます。

- **引数:**
    - `pulse` (`int`): 設定するパルス幅 (マイクロ秒)。

### `move_min(self)`

サーボモーターを最小位置に移動させます。パルス幅を `MIN` に設定します。

### `move_max(self)`

サーボモーターを最大位置に移動させます。パルス幅を `MAX` に設定します。

### `move_center(self)`

サーボモーターを中央位置に移動させます。パルス幅を `CENTER` に設定します。

### `off(self)`

サーボモーターの電源をオフにします。パルス幅を `0` に設定して動作を停止させます。

### `get_pulse(self)`

現在のサーボモーターのパルス幅を取得します。

- **戻り値:**
    - `int`: 現在のパルス幅 (マイクロ秒)。