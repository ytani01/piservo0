# `piservo0` API Reference

このドキュメントは、`piservo0`ライブラリのAPIリファレンスです。
ライブラリは以下の主要なクラスで構成されています。

- **`PiServo`**: サーボモーターを直接制御する基本クラス。
- **`CalibrableServo`**: `PiServo`を拡張し、キャリブレーション機能を追加したクラス。
- **`MultiServo`**: 複数のサーボモーターを同期制御するクラス。
- **`ServoConfigManager`**: サーボの設定をJSONファイルで管理するクラス。
- **`StrControl`**: 文字列ベースのコマンドを解釈し、複数のサーボモーターを制御するクラス。
- **`ThreadWorker`**: 別スレッドでサーボ制御コマンドを実行するワーカークラス。

---

## `PiServo` クラス

Raspberry PiのGPIOピンを介してサーボモーターを制御する基本クラスです。`pigpio`ライブラリを利用してパルス幅を直接設定します。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `OFF` | `0` | サーボをオフにするためのパルス幅 |
| `MIN` | `500` | デフォルトの最小パルス幅 (マイクロ秒) |
| `MAX` | `2500` | デフォルトの最大パルス幅 (マイクロ秒) |
| `CENTER`| `1500`| デフォルトの中央位置のパルス幅 (マイクロ秒) |

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
| `DEF_CONF_FILE` | `'./servo.json'` | デフォルトの設定ファイル名 |
| `ANGLE_MIN` | `-90.0` | 最小角度 |
| `ANGLE_MAX` | `90.0` | 最大角度 |
| `ANGLE_CENTER`| `0.0`| 中央角度 |
| `POS_CENTER`| `'center'`| 中央位置を示す文字列 |
| `POS_MIN`| `'min'`| 最小位置を示す文字列 |
| `POS_MAX`| `'max'`| 最大位置を示す文字列 |

### `__init__(self, pi, pin, conf_file=DEF_CONF_FILE, debug=False)`

`CalibrableServo`オブジェクトを初期化します。設定ファイルからキャリブレーション値を読み込みます。

- **引数:**
    - `pi` (`pigpio.pi`): `pigpio.pi`のインスタンス。
    - `pin` (`int`): サーボが接続されているGPIOピン番号。
    - `conf_file` (`str`, optional): キャリブレーション設定ファイルのパス。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。

### プロパティ

- **`pulse_min`** (`int`): キャリブレーションされた最小のパルス幅。設定時には`save_conf()`が自動的に呼び出されます。
- **`pulse_center`** (`int`): キャリブレーションされた中央のパルス幅。設定時には`save_conf()`が自動的に呼び出されます。
- **`pulse_max`** (`int`): キャリブレーションされた最大のパルス幅。設定時には`save_conf()`が自動的に呼び出されます。

### メソッド

- **`move_pulse(self, pulse, forced=False)`**: キャリブレーション範囲内でパルス移動します。`forced=True`の場合、範囲外でも移動します。
- **`move_min(self)`**: キャリブレーションされた最小位置へ移動します。
- **`move_max(self)`**: キャリブレーションされた最大位置へ移動します。
- **`move_center(self)`**: キャリブレーションされた中央位置へ移動します。
- **`move_angle(self, deg)`**: 指定された角度 (`-90.0`～`90.0`) にサーボを移動させます。文字列 (`'center'`, `'min'`, `'max'`) で指定することも可能です。
- **`get_angle(self)`**: 現在のサーボの角度を取得します。
- **`deg2pulse(self, deg)`**: 角度をパルス幅に変換します。
- **`pulse2deg(self, pulse)`**: パルス幅を角度に変換します。
- **`load_conf(self)`**: ファイルから設定を読み込みます。
- **`save_conf(self)`**: 現在の設定をファイルに保存します。

---

## `MultiServo` クラス

複数の`CalibrableServo`を同時に、または同期して制御するためのクラスです。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `DEF_ESTIMATED_TIME` | `0.2` | 同期移動のデフォルト推定時間 (秒) |
| `DEF_STEP_N` | `40` | 同期移動のデフォルト分割ステップ数 |

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
    - `target_angles` (`list[float]`): 目標角度のリスト。数値、または`CalibrableServo.POS_CENTER`, `CalibrableServo.POS_MIN`, `CalibrableServo.POS_MAX`のような文字列、`None` (動かさない) を指定可能。
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

## `StrControl` クラス

文字列ベースのコマンドを解釈し、複数のサーボモーター（`MultiServo`）を制御するクラスです。
'fbcb' のような文字列は、各サーボのポーズ（姿勢）を示します。
コマンド文字を大文字（例: 'FBCB'）にすると、角度が2倍になります。
コマンド（例: 'fbcb' や '0.5'）を実行することで、ロボットの歩行などの複雑な動作を簡単に実現できます。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `DEF_ANGLE_UNIT` | `30.0` | 'forward'/'backward'のデフォルト基本角度 (度) |
| `DEF_MODE_SEC` | `0.2` | 1ポーズのデフォルト移動時間 (秒) |
| `DEF_CMD_CHARS` | `{'center': 'c', 'min': 'n', 'max': 'x', 'forward': 'f', 'backward': 'b', 'dont_move': '.'}` | コマンド文字のデフォルト定義 |

### `__init__(self, mservo, angle_unit=DEF_ANGLE_UNIT, move_sec=DEF_MODE_SEC, step_n=MultiServo.DEF_STEP_N, angle_factor=None, cmd_chars=None, debug=False)`

`StrControl`オブジェクトを初期化します。

- **引数:**
    - `mservo` (`MultiServo`): 制御対象の`MultiServo`オブジェクト。
    - `angle_unit` (`float`, optional): 'forward'/'backward'の基本角度。デフォルトは`DEF_ANGLE_UNIT`。
    - `move_sec` (`float`, optional): 1ポーズの移動にかける時間（秒）。デフォルトは`DEF_MODE_SEC`。
    - `step_n` (`int`, optional): 同期移動の分割ステップ数。デフォルトは`MultiServo.DEF_STEP_N`。
    - `angle_factor` (`list[int] | None`, optional): 各サーボの角度に掛ける係数のリスト。サーボの回転方向を反転させるのに使います。`None`の場合、すべての要素が`1`になります。
    - `cmd_chars` (`dict[str, str] | None`, optional): ポーズを定義する文字をカスタムする場合に指定します。`None`の場合、`DEF_CMD_CHARS`が使用されます。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。デフォルトは`False`。

### メソッド

- **`set_angle_unit(self, angle)`**: 'forward'/'backward'の基本角度を設定します。
- **`set_move_sec(self, sec)`**: 1ポーズの移動時間を設定します。
- **`parse_cmd(self, cmd)`**: 単一のコマンド文字列を解析し、実行可能な辞書形式に変換します。
    - **引数**: `cmd` (`str`) - 'fbcb'のようなポーズ文字列、または'0.5'のような数値文字列（スリープ時間）。ポーズ文字列で大文字を使用すると、そのサーボの角度が2倍になります。
    - **戻り値**: `dict` - 解析結果。例: `{'cmd': 'angles', 'angles': [-40, 0, -40, 0]}`、`{'cmd': 'sleep', 'sec': 0.5}`、`{'cmd': 'error', 'err': 'invalid command'}`。
- **`exec_cmd(self, cmd)`**: 単一のコマンドを実行します。
    - **引数**: `cmd` (`str`) - ポーズ文字列またはスリープ時間。ポーズ文字列で大文字を使用すると、そのサーボの角度が2倍になります。
- **`flip_cmds(cmds)`**: コマンド文字列を左右反転させたシーケンスを返します。
    - **引数**: `cmds` (`list[str]`) - コマンドシーケンス。
    - **戻り値**: `list[str]` - 反転されたコマンドシーケンス。例: `['fcfb']` -> `['bfcf']`。

---

## `ThreadWorker` クラス

別スレッドでサーボ制御コマンドを実行するためのワーカークラスです。
コマンドキューを介してコマンドを受け取り、非同期にサーボを制御します。

### クラス定数

| 定数名 | 値 | 説明 |
|---|---|---|
| `DEF_RECV_TIMEOUT` | `0.2` | コマンド受信のデフォルトタイムアウト (秒) |
| `DEF_INTERVAL_SEC` | `0.0` | コマンド実行間のデフォルトインターバル (秒) |

### `__init__(self, mservo, move_sec=None, step_n=None, interval_sec=DEF_INTERVAL_SEC, debug=False)`

`ThreadWorker`オブジェクトを初期化します。

- **引数:**
    - `mservo` (`MultiServo`): 制御対象の`MultiServo`オブジェクト。
    - `move_sec` (`float | None`, optional): 1ポーズの移動にかける時間（秒）。`None`の場合、`MultiServo.DEF_ESTIMATED_TIME`が使用されます。
    - `step_n` (`int | None`, optional): 同期移動の分割ステップ数。`None`の場合、`MultiServo.DEF_STEP_N`が使用されます。
    - `interval_sec` (`float`, optional): コマンド実行間のインターバル（秒）。デフォルトは`DEF_INTERVAL_SEC`。
    - `debug` (`bool`, optional): デバッグログを有効にするフラグ。デフォルトは`False`。

### メソッド

- **`end(self)`**: ワーカーを終了し、スレッドを停止します。
- **`cmdq_clear(self)`**: コマンドキューをクリアします。
- **`send(self, cmd)`**: コマンドをキューに送信します。
    - **引数**: `cmd` (`dict` or `str`) - 実行するコマンド。辞書形式（例: `{'cmd': 'angles', 'angles': [30, 0, -30, 0]}`）またはJSON文字列。
- **`recv(self, timeout=DEF_RECV_TIMEOUT)`**: コマンドキューからコマンドを受信します。
    - **引数**: `timeout` (`float`, optional) - 受信タイムアウト時間（秒）。
    - **戻り値**: `dict` or `str` - 受信したコマンド、またはタイムアウトした場合は空文字列。
- **`run(self)`**: スレッドのメインループ。キューからコマンドを読み込み、実行します。
    - このメソッドは直接呼び出すのではなく、`ThreadWorker`インスタンスの`start()`メソッドによって自動的に呼び出されます。

---

## `my_logger` モジュール

シンプルなロガーを生成するためのヘルパー関数を提供します。

### `get_logger(name, dbg=False)`

ロガーを取得します。

- **引数:**
    - `name` (`str`): ロガーの名前。
    - `dbg` (`bool` or `int`): `True`にするとデバッグレベル(`DEBUG`)になります。ロギングレベルを直接指定することも可能です。
- **戻り値**: `logging.Logger` - 設定済みのロガーインスタンス。
