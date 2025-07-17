# `piservo0` API Reference

このドキュメントは、`piservo0`ライブラリのAPIリファレンスです。
ライブラリは以下の主要なクラスで構成されています。

- **`PiServo`**: サーボモーターを直接制御する基本クラス。
- **`CalibrableServo`**: `PiServo`を拡張し、キャリブレーション機能を追加したクラス。
- **`MultiServo`**: 複数のサーボモーターを同期制御するクラス。
- **`ServoConfigManager`**: サーボの設定をJSONファイルで管理するクラス。

---

## `PiServo` クラス

Raspberry PiのGPIOピンを介してサーボモーターを制御する基本クラスです。`pigpio`ライブラリを利用してパルス幅を直接設定します。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `OFF` | `0` | サーボをオフにするためのパルス幅 |
| `MIN` | `500` | デフォルトの最小パルス幅 (マイクロ秒) |
| `MAX` | `2500` | デフォルトの最大パルス幅 (マイクロ秒) |
| `CENTER`| `1450`| デフォルトの中央位置のパルス幅 (マイクロ秒) |

### `__init__(self, pi, pin, debug=False)`

`PiServo`オブジェクトを初期化します。

- **引数:**
    - `pi` (`pigpio.pi`): `pigpio.pi`のインスタンス。
    - `pin` (`int`): サーボが接続されているGPIOピン番号。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。デフォルトは`False`。

### メソッド

- **`move_pulse(self, pulse)`**: 指定されたパルス幅にサーボを移動させます。パルス幅が`MIN`と`MAX`の範囲外の場合、自動的に範囲内に調整されます。
- **`move_min(self)`**: サーボを最小位置 (`MIN`) に移動させます。
- **`move_max(self)`**: サーボを最大位置 (`MAX`) に移動させます。
- **`move_center(self)`**: サーボを中央位置 (`CENTER`) に移動させます。
- **`off(self)`**: サーボの電源をオフにします (パルス幅を`OFF`に設定)。
- **`get_pulse(self)`**: 現在のサーボのパルス幅を取得します。
    - **戻り値**: `int` - 現在のパルス幅 (マイクロ秒)。

---

## `CalibrableServo` クラス

`PiServo`を継承し、各サーボの個体差を吸収するためのキャリブレーション機能を追加したクラスです。設定は`ServoConfigManager`を通じてJSONファイルに永続化されます。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `DEF_CONF_FILE` | `'./servo.json'` | デフォルトの設��ファイル名 |
| `ANGLE_MIN` | `-90.0` | 最小角度 |
| `ANGLE_MAX` | `90.0` | 最大角度 |
| `ANGLE_CENTER`| `0.0`| 中央角度 |

### `__init__(self, pi, pin, conf_file=DEF_CONF_FILE, debug=False)`

`CalibrableServo`オブジェクトを初期化します。設定ファイルからキャリブレーション値を読み込みます。

- **引数:**
    - `pi` (`pigpio.pi`): `pigpio.pi`のインスタンス。
    - `pin` (`int`): サーボが接続されているGPIOピン番号。
    - `conf_file` (`str`, optional): キャリブレーション設定ファイルのパス。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。

### プロパティ

- **`min`, `center`, `max`** (`int`): キャリブレーションされた最小、中央、最大のパルス幅。

### 移動メソッド

- **`move_pulse(self, pulse, forced=False)`**: キャリブレーション範囲内でパルス移動します。`forced=True`の場合、範囲外でも移動します。
- **`move_min(self)`**: キャリブレーションされた最小位置へ移動します。
- **`move_max(self)`**: キャリブレーションされた最大位置へ移動します。
- **`move_center(self)`**: キャリブレーションされた中央位置へ移動します。
- **`move_angle(self, deg)`**: 指定された角度 (`-90.0`～`90.0`) にサーボを移動させます。

### 角度・パルス幅関連メソッド

- **`get_angle(self)`**: 現在のサーボの角度を取得します。
- **`deg2pulse(self, deg)`**: 角度をパルス幅に変換します。
- **`pulse2deg(self, pulse)`**: パルス幅を角度に変換します。

### キャリブレーション設定メソッド

現在のサーボ位置を基にキャリブレーション値を設定し、ファイルに保存します。

- **`set_min(self, pulse=None)`**: 最小位置を設定します。
- **`set_max(self, pulse=None)`**: 最大位置を設定します。
- **`set_center(self, pulse=None)`**: 中央位置を設定します。

### 設定ファイル管理メソッド

- **`load_conf(self)`**: ファイルから設定を読み込みます。
- **`save_conf(self)`**: 現在の設定をファイルに保存します。

---

## `MultiServo` クラス

複数の`CalibrableServo`を同時に、または同期して制御するためのクラスです。

### `__init__(self, pi, pins, first_move=True, conf_file=CalibrableServo.DEF_CONF_FILE, debug=False)`

`MultiServo`オブジェクトを初期化します。

- **引数:**
    - `pi` (`pigpio.pi`): `pigpio.pi`のインスタンス。
    - `pins` (`list[int]`): 制御するサーボのGPIOピン番号のリスト。
    - `first_move` (`bool`, optional): 初期化時にサーボを中央(0度)に移動させるか。デフォルトは`True`。
    - `conf_file` (`str`, optional): キャリブレーション設定ファイルのパス。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。

### メソッド

- **`off(self)`**: すべてのサーボをオフにします。
- **`get_pulse(self)`**: 全サーボの現在のパルス幅をリストで取得します。
- **`move_pulse(self, pulses, forced=False)`**: 全サーボをそれぞれのパルス幅に移動させます。
- **`get_angle(self)`**: 全サーボの現在の角度をリストで取得します。
- **`move_angle(self, angles)`**: 全サーボをそれぞれの角度に移動させます。
- **`move_angle_sync(self, target_angles, estimated_sec=1.0, step_n=50)`**: 全サーボを目標角度まで同期的に滑らかに移動させます。
    - `target_angles` (`list[float]`): 目標角度のリスト。
    - `estimated_sec` (`float`): 移動にかかるおおよその時間。
    - `step_n` (`int`): 移動の分割ステップ数。

---

## `ServoConfigManager` クラス

サーボのキャリブレーション設定をJSONファイルとして読み書きする責務を担うクラスです。

### `__init__(self, conf_file, debug=False)`

`ServoConfigManager`オブジェクトを初期化します。

- **引数:**
    - `conf_file` (`str`): 設定ファイルのパス。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。

### メソッド

- **`read_all_configs(self)`**: 設定ファイルからすべてのピンのデータを読み込みます。
    - **戻り値**: `list` - 設定データのリスト。
- **`save_all_configs(self, data)`**: すべてのピンのデータをファイルに書き込みます。データはピン番号でソートされます。
- **`get_config(self, pin)`**: 指定されたピンの設定を読み込みます。
    - **戻り値**: `dict | None` - ピンの設定データ。
- **`save_config(self, new_pindata)`**: 指定されたピンの設定を更新または追加して保存します。

---

## `my_logger` モジュール

シンプルなロガーを生成するためのヘルパー関数を提供します。

### `get_logger(name, dbg=False)`

ロガーを取得します。

- **引数:**
    - `name` (`str`): ロガーの名前。
    - `dbg` (`bool` or `int`): `True`にするとデバッグレベル(`DEBUG`)になります。ロギングレベルを直接指定することも可能です。
- **戻り値**: `logging.Logger` - 設定済みのロガーインスタンス。
