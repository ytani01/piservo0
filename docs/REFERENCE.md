# `piservo0` API Reference

このドキュメントは、`piservo0`ライブラリのAPIリファレンスです。
ライブラリは以下の主要なクラスで構成されています。

-   **`PiServo`**: サーボモーターを直接制御する基本クラス。
-   **`CalibrableServo`**: `PiServo`を拡張し、キャリブレーション機能を追加したクラス。
-   **`MultiServo`**: 複数のサーボモーターを同期制御するクラス。
-   **`ThreadMultiServo`**: `MultiServo`を非同期で制御するためのインターフェースクラス。
-   **`StrControl`**: 文字列ベースのコマンドで `MultiServo` を制御するヘルパークラス。
-   **`ServoConfigManager`**: サーボの設定をJSONファイルで管理するユーティリティクラス。
-   **`ThreadWorker`**: 別スレッドでサーボ制御コマンドを実行するワーカークラス。
-   **`my_logger`**: ログ出力のためのユーティリティ関数。

---

## `core` モジュール

### `PiServo` クラス

Raspberry PiのGPIOピンを介してサーボモーターを制御する基本クラスです。`pigpio`ライブラリを利用してパルス幅を直接設定します。

#### クラス定数

| 定数名     | 値     | 説明                                   |
| :--------- | :----- | :------------------------------------- |
| `OFF`      | `0`    | サーボをオフにするためのパルス幅       |
| `MIN`      | `500`  | デフォルトの最小パルス幅 (マイクロ秒)  |
| `MAX`      | `2500` | デフォルトの最大パルス幅 (マイクロ秒)  |
| `CENTER`   | `1500` | デフォルトの中央位置のパルス幅 (マイクロ秒) |

#### `__init__(self, pi, pin, debug=False)`

`PiServo`オブジェクトを初期化します。

-   **引数:**
    -   `pi` (`pigpio.pi`): `pigpio.pi`のインスタンス。
    -   `pin` (`int`): サーボが接続されているGPIOピン番号。
    -   `debug` (`bool`, optional): デバッグログを有効にするフラグ。デフォルトは`False`。

#### メソッド

-   **`move_pulse(self, pulse)`**: 指定されたパルス幅にサーボを移動させます。パルス幅が`MIN`と`MAX`の範囲外の場合、自動的に範囲内に調整されます。
-   **`move_min(self)`**: サーボを最小位置 (`MIN`) に移動させます。
-   **`move_max(self)`**: サーボを最大位置 (`MAX`) に移動させます。
-   **`move_center(self)`**: サーボを中央位置 (`CENTER`) に移動させます。
-   **`off(self)`**: サーボの電源をオフにします (パルス幅を`OFF`に設定)。
-   **`get_pulse(self)`**: 現在のサーボのパルス幅を取得します。
    -   **戻り値**: `int` - 現在のパルス幅 (マイクロ秒)。

---

### `CalibrableServo` クラス

`PiServo`を継承し、各サーボの個体差を吸収するためのキャリブレーション機能を追加したクラスです。設定は`ServoConfigManager`を通じてJSONファイルに永続化されます。

#### クラス定数

| 定数名          | 値             | 説明                       |
| :-------------- | :------------- | :------------------------- |
| `DEF_CONF_FILE` | `'servo.json'` | デフォルトの設定ファイル名 |
| `ANGLE_MIN`     | `-90.0`        | 最小角度                   |
| `ANGLE_MAX`     | `90.0`         | 最大角度                   |
| `ANGLE_CENTER`  | `0.0`          | 中央角度                   |
| `POS_CENTER`    | `'center'`     | 中央位置を示す文字列       |
| `POS_MIN`       | `'min'`        | 最小位置を示す文字列       |
| `POS_MAX`       | `'max'`        | 最大位置を示す文字列       |

#### `__init__(self, pi, pin, conf_file=DEF_CONF_FILE, debug=False)`

`CalibrableServo`オブジェクトを初期化します。設定ファイルからキャリブレーション値を読み込みます。

-   **引数:**
    -   `pi` (`pigpio.pi`): `pigpio.pi`のインスタンス。
    -   `pin` (`int`): サーボが接続されているGPIOピン番号。
    -   `conf_file` (`str`, optional): キャリブレーション設定ファイルのパス。
    -   `debug` (`bool`, optional): デバッグログを有効にするフラグ。

#### プロパティ

-   **`pulse_min`** (`int`): キャリブレーションされた最小のパルス幅。設定時には`save_conf()`が自動的に呼び出されます。
-   **`pulse_center`** (`int`): キャリブレーションされた中央のパルス幅。設定時には`save_conf()`が自動的に呼び出されます。
-   **`pulse_max`** (`int`): キャリブレーションされた最大のパルス幅。設定時には`save_conf()`が自動的に呼び出されます。

#### メソッド

-   **`move_pulse(self, pulse, forced=False)`**: キャリブレーション範囲内でパルス移動します。`forced=True`の場合、範囲外でも移動します。
-   **`move_min(self)`**: キャリブレーションされた最小位置へ移動します。
-   **`move_max(self)`**: キャリブレーションされた最大位置へ移動します。
-   **`move_center(self)`**: キャリブレーションされた中央位置へ移動します。
-   **`move_angle(self, deg)`**: 指定された角度 (`-90.0`～`90.0`) にサーボを移動させます。文字列 (`'center'`, `'min'`, `'max'`) で指定することも可能です。
-   **`get_angle(self)`**: 現在のサーボの角度を取得します。
-   **`deg2pulse(self, deg)`**: 角度をパルス幅に変換します。
-   **`pulse2deg(self, pulse)`**: パルス幅を角度に変換します。
-   **`load_conf(self)`**: ファイルから設定を読み込みます。
-   **`save_conf(self)`**: 現在の設定をファイルに保存します。

---

### `MultiServo` クラス

複数の`CalibrableServo`を同時に、または同期して制御するためのクラスです。

#### クラス定数

| 定数名         | 値    | 説明                               |
| :------------- | :---- | :--------------------------------- |
| `DEF_MOVE_SEC` | `0.2` | 同期移動のデフォルト時間 (秒)      |
| `DEF_STEP_N`   | `40`  | 同期移動のデフォルト分割ステップ数 |

#### `__init__(self, pi, pins, first_move=True, conf_file=CalibrableServo.DEF_CONF_FILE, debug=False)`

`MultiServo`オブジェクトを初期化します。

-   **引数:**
    -   `pi` (`pigpio.pi`): `pigpio.pi`のインスタンス。
    -   `pins` (`list[int]`): 制御するサーボのGPIOピン番号のリスト。
    -   `first_move` (`bool`, optional): 初期化時にサーボを中央(0度)に移動させるか。デフォルトは`True`。
    -   `conf_file` (`str`, optional): キャリブレーション設定ファイルのパス。
    -   `debug` (`bool`, optional): デバッグログを有効にするフラグ。

#### メソッド

-   **`off(self)`**: すべてのサーボをオフにします。
-   **`get_pulse(self)`**: 全サーボの現在のパルス幅をリストで取得します。
-   **`move_pulse(self, pulses, forced=False)`**: 全サーボをそれぞれのパルス幅に移動させます。
-   **`get_angle(self)`**: 全サーボの現在の角度をリストで取得します。
-   **`move_angle(self, angles)`**: 全サーボをそれぞれの角度に移動させます。
-   **`move_angle_sync(self, target_angles, move_sec=DEF_MOVE_SEC, step_n=DEF_STEP_N)`**: 全サーボを目標角度まで同期的に滑らかに移動させます。
    -   `target_angles` (`list[float]`): 目標角度のリスト。数値、または`CalibrableServo.POS_CENTER`, `CalibrableServo.POS_MIN`, `CalibrableServo.POS_MAX`のような文字列、`None` (動かさない) を指定可能。
    -   `move_sec` (`float`): 移動にかかる時間。
    -   `step_n` (`int`): 移動の分割ステップ数。

---

## `utils` モジュール

### `ServoConfigManager` クラス

サーボのキャリブレーション設定をJSONファイルとして読み書きする責務を担うクラスです。

#### `__init__(self, conf_file, debug=False)`

`ServoConfigManager`オブジェクトを初期化します。

-   **引数:**
    -   `conf_file` (`str`): 設定ファイルのパス。
        -   **パス指定の挙動:**
            -   `./` や `../` を含む相対パス、または絶対パスで指定された場合、そのパスがそのまま使われます。
            -   ファイル名のみが指定された場合、以下の優先順位でファイルを検索します。
                1.  カレントディレクトリ
                2.  ホームディレクトリ (`~/`)
                3.  `/etc/`
        -   いずれの場所にもファイルが見つからない場合、カレントディレクトリに新しい設定ファイルが作成される際のパスとして扱われます。
    -   `debug` (`bool`, optional): デバッグログを有効にするフラグ。

#### メソッド

-   **`read_all_configs(self)`**: 設定ファイルからすべてのピンのデータを読み込みます。
    -   **戻り値**: `list` - 設定データのリスト。
-   **`save_all_configs(self, data)`**: すべてのピンのデータをファイルに書き込みます。データはピン番号でソートされます。
-   **`get_config(self, pin)`**: 指定されたピンの設定を読み込みます。
    -   **戻り値**: `dict | None` - ピンの設定データ。
-   **`save_config(self, new_pindata)`**: 指定されたピンの設定を更新または追加して保存します。

---

### `my_logger` モジュール

シンプルなロガーを生成するためのヘルパー関数を提供します。

#### `get_logger(name, debug=False)`

ロガーを取得します。

-   **引数:**
    -   `name` (`str`): ロガーの名前。
    -   `debug` (`bool` or `int`): `True`にするとデバッグレベル(`DEBUG`)になります。ロギングレベルを直接指定することも可能です。
-   **戻り値**: `logging.Logger` - 設定済みのロガーインスタンス。

---

## `helper` モジュール

### `StrControl` クラス

文字列ベースのコマンドを解釈し、複数のサーボモーター（`MultiServo`）を制御するクラスです。
'fbcb' のような文字列は、各サーボのポーズ（姿勢）を示します。コマンド文字を大文字（例: 'F'）にすると、そのサーボに設定される角度が2倍になります。
コマンド（例: 'fbcb' や '0.5'）を実行することで、ロボットの歩行などの複雑な動作を簡単に実現できます。

#### クラス定数

| 定数名          | 値                                                                                             | 説明                                           |
| :-------------- | :--------------------------------------------------------------------------------------------- | :--------------------------------------------- |
| `DEF_ANGLE_UNIT`| `30.0`                                                                                         | 'forward'/'backward'のデフォルト基本角度 (度)  |
| `DEF_MODE_SEC`  | `0.2`                                                                                          | 1ポーズのデフォルト移動時間 (秒)               |
| `DEF_CMD_CHARS` | `{'center': 'c', 'min': 'n', 'max': 'x', 'forward': 'f', 'backward': 'b', 'dont_move': '.'}` | コマンド文字のデフォルト定義                   |

#### `__init__(self, mservo, angle_unit=DEF_ANGLE_UNIT, move_sec=DEF_MODE_SEC, step_n=MultiServo.DEF_STEP_N, angle_factor=None, cmd_chars=None, debug=False)`

`StrControl`オブジェクトを初期化します。

-   **引数:**
    -   `mservo` (`MultiServo` | `ThreadMultiServo`): 制御対象のオブジェクト。同期・非同期どちらのインスタンスも指定可能です。
    -   `angle_unit` (`float`, optional): 'forward'/'backward'の基本角度。
    -   `move_sec` (`float`, optional): 1ポーズの移動にかける時間（秒）。
    -   `step_n` (`int`, optional): 同期移動の分割ステップ数。
    -   `angle_factor` (`list[int] | None`, optional): 各サーボの角度に掛ける係数のリスト。サーボの回転方向を反転させるのに使います。`None`の場合、すべての要素が`1`になります。
    -   `cmd_chars` (`dict[str, str] | None`, optional): ポーズを定義する文字をカスタムする場合に指定します。
    -   `debug` (`bool`, optional): デバッグログを有効にするフラグ。

#### メソッド

-   **`set_angle_unit(self, angle)`**: 'forward'/'backward'の基本角度を設定します。
-   **`set_move_sec(self, sec)`**: 1ポーズの移動時間を設定します。
-   **`parse_cmd(self, cmd)`**: 単一のコマンド文字列を解析し、実行可能な辞書形式に変換します。
    -   **引数**: `cmd` (`str`) - 'fbcb'のようなポーズ文字列、または'0.5'のような数値文字列（スリープ時間）。ポーズ文字列で大文字を使用すると、そのサーボの角度が2倍になります。
    -   **戻り値**: `dict` - 解析結果。例: `{'cmd': 'move_angle_sync', 'target_angles': [-30.0, 30.0, -30.0, 30.0], ...}`、`{'cmd': 'sleep', 'sec': 0.5}`。
-   **`exec_cmd(self, cmd)`**: 単一のコマンドを実行します。
-   **`flip_cmds(cmds)` (staticmethod)**: コマンド文字列を左右反転させたシーケンスを返します。
    -   **引数**: `cmds` (`list[str]`) - コマンドシーケンス。
    -   **戻り値**: `list[str]` - 反転されたコマンドシーケンス。例: `['fcfb']` -> `['bfcf']`。

---

### `ThreadWorker` クラス

別スレッドでサーボ制御コマンドを実行するためのワーカークラスです。
コマンドキューを介してコマンドを受け取り、非同期にサーボを制御します。通常、`ThreadMultiServo`クラスを通じて間接的に利用されます。

#### クラス定数

| 定数名             | 値    | 説明                                       |
| :----------------- | :---- | :----------------------------------------- |
| `DEF_RECV_TIMEOUT` | `0.2` | コマンド受信のデフォルトタイムアウト (秒)  |
| `DEF_INTERVAL_SEC` | `0.0` | コマンド実行間のデフォルトインターバル (秒)|

#### `__init__(self, mservo, move_sec=None, step_n=None, interval_sec=DEF_INTERVAL_SEC, debug=False)`

`ThreadWorker`オブジェクトを初期化します。

-   **引数:**
    -   `mservo` (`MultiServo`): 制御対象の`MultiServo`オブジェクト。
    -   `move_sec` (`float | None`, optional): 1ポーズの移動にかける時間（秒）。`None`の場合、`MultiServo.DEF_MOVE_SEC`が使用されます。
    -   `step_n` (`int | None`, optional): 同期移動の分割ステップ数。`None`の場合、`MultiServo.DEF_STEP_N`が使用されます。
    -   `interval_sec` (`float`, optional): コマンド実行間のインターバル（秒）。
    -   `debug` (`bool`, optional): デバッグログを有効にするフラグ。

#### メソッド

-   **`end(self)`**: ワーカーを終了し、スレッドを停止します。
-   **`clear_cmdq(self)`**: コマンドキューをクリアします。
-   **`send(self, cmd)`**: コマンドをキューに送信します。
    -   **引数**: `cmd` (`dict` or `str`) - 実行するコマンド。辞書形式またはJSON文字列。
-   **`recv(self, timeout=DEF_RECV_TIMEOUT)`**: コマンドキューからコマンドを受信します。
-   **`run(self)`**: スレッドのメインループ。キューからコマンドを読み込み、実行します。`start()`メソッドによって自動的に呼び出されます。

#### 受け付けるコマンド形式

`send()`メソッドには、以下のようなキーを持つ辞書（またはそのJSON文字列）を渡します。

-   `cmd` (`str`): 実行するコマンド名。
-   その他、コマンドに応じた引数。

以下に、利用可能なコマンドの例を示します。

-   **`move_angle_sync`**: 全サーボを目標角度まで同期的に滑らかに移動させます。
    -   `target_angles` (`list`): 目標角度のリスト。
    -   `move_sec` (`float`, optional): 移動時間。省略時は現在の設定値が使われます。
    -   `step_n` (`int`, optional): 分割ステップ数。省略時は現在の設定値が使われます。
    ```json
    {"cmd": "move_angle_sync", "target_angles": [0, 45, -45, 0], "move_sec": 0.5, "step_n": 50}
    ```

-   **`move_angle`**: 全サーボを目標角度に即座に移動させます。
    -   `target_angles` (`list`): 目標角度のリスト。
    ```json
    {"cmd": "move_angle", "target_angles": [90, 90, 90, 90]}
    ```

-   **`move_sec`**: `move_angle_sync`のデフォルト移動時間を設定します。
    ```json
    {"cmd": "move_sec", "sec": 1.0}
    ```

-   **`step_n`**: `move_angle_sync`のデフォルト分割ステップ数を設定します。
    ```json
    {"cmd": "step_n", "n": 100}
    ```

-   **`interval`**: 各コマンド実行後の待機時間を設定します。
    ```json
    {"cmd": "interval", "sec": 0.1}
    ```

-   **`sleep`**: 指定された時間、ワーカースレッドを休止させます。
    ```json
    {"cmd": "sleep", "sec": 2.0}
    ```

---

### `ThreadMultiServo` クラス

サーボモーター群を非同期で制御するためのインターフェースクラスです。内部で `MultiServo` と `ThreadWorker` を協調させて動作します。
このクラスのメソッドはすべて非同期であり、呼び出し元をブロックしません。

#### `__init__(self, pi, pins, first_move=True, conf_file=CalibrableServo.DEF_CONF_FILE, debug=False)`

`ThreadMultiServo`のインスタンスを初期化します。

-   **引数:**
    -   `pi`: `pigpio.pi`のインスタンス。
    -   `pins` (`list[int]`): サーボを接続したGPIOピンのリスト。
    -   `first_move` (`bool`, optional): 初期化時にサーボを0度の位置に移動させます。デフォルトは`True`。
    -   `conf_file` (`str`, optional): キャリブレーション設定ファイルのパス。
    -   `debug` (`bool`, optional): デバッグモードを有効にするかどうかのフラグ。デフォルトは`False`。

#### プロパティ

-   **`pins`** (`list[int]`): サーボが接続されているGPIOピンのリスト。
-   **`conf_file`** (`str`): 使用している設定ファイルのパス。

#### メソッド

-   **`end(self)`**: 終了処理。ワーカースレッドを安全に停止させ、すべてのサーボをオフにします。このメソッドは同期的です。
-   **`off(self)`**: `end()`のエイリアスです。
-   **`move_angle(self, target_angles)`**: 指定された角度に即座に移動するコマンドを非同期で送信します。
-   **`move_angle_sync(self, target_angles, move_sec=None, step_n=None)`**: 目標角度まで滑らかに移動するコマンドを非同期で送信します。
-   **`set_move_sec(self, sec)`**: 移動時間を設定するコマンドを非同期で送信します。
-   **`set_step_n(self, n)`**: ステップ数を設定するコマンドを非同期で送信します。
-   **`set_interval(self, sec)`**: コマンド実行後のインターバルを設定するコマンドを非同期で送信します。
-   **`sleep(self, sec)`**: 指定時間スリープするコマンドを非同期で送信します。
-   **`get_pulse(self)`**: すべてのサーボの現在のパルス幅を取得します。
-   **`get_angle(self)`**: すべてのサーボの現在の角度を取得します。