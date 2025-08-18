# APIリファレンス

このドキュメントは `piservo0` ライブラリが提供する主要なクラスとメソッドの詳細な仕様を記述します。

## クラス階層(is-a)

```
(builtins.object)
  |
  +-- Piservo
  |     |
  |     +-- CalibrableServo
  |
  +-- MultiServo
  |
  +-- ThreadMultiServo
  |
  +-- StrCmdToJson
  |
  +-- (threading.Thread)
        |
        +-- ThreadWorker
```

## クラス関係(has-a)

```
ThreadWorker
  |
  +--  MultiServo
         |
         +-- CalibrableServo(PiServo)
               |
               +-- pigpio.pi
```

---

## class `PiServo`

サーボモーターを制御するための最も基本的なクラスです。`pigpio`ライブラリのラッパーとして機能し、パルス幅を指定して直接的にサーボを動かします。

### サンプルプログラム

- [sample_01_piservo.py](samples/sample_01_piservo.py)

### `PiServo(pi, pin, debug=False)`
- **説明**: `PiServo`のインスタンスを初期化します。
- **引数**:
    - `pi (pigpio.pi)`: `pigpio`のインスタンス。
    - `pin (int)`: サーボが接続されているGPIOピン番号。
    - `debug (bool)`: デバッグログを有効にするかどうかのフラグ。

### `move_pulse(pulse)`
- **説明**: 指定されたパルス幅にサーボを移動させます。パルス幅は `MIN` (500) から `MAX` (2500) の範囲に制限されます。
- **引数**:
    - `pulse (int)`: マイクロ秒単位のパルス幅。

### `move_pulse_relative(pulse_diff)`
- **説明**: 現在のパルス幅から、指定した値だけ相対的にサーボを動かします。
- **引数**:
    - `pulse_diff (int)`: パルス幅の変化量。

### `get_pulse()`
- **説明**: 現在のサーボのパルス幅を取得します。
- **戻り値**: `int` - 現在のパルス幅。

### `off()`
- **説明**: サーボモーターへの電力供給を停止します（パルス幅を0に設定）。

---

## class `CalibrableServo`

`PiServo`を継承し、キャリブレーション機能を追加したクラスです。サーボモーターの個体差を吸収し、より正確な角度制御を可能にします。

### サンプルプログラム

- [sample_02_calibrable_servo.py](samples/sample_02_calibrable_servo.py)

### `CalibrableServo(pi, pin, conf_file='servo.json', debug=False)`
- **説明**: `CalibrableServo`のインスタンスを初期化します。設定ファイルが存在すれば読み込み、なければデフォルト値で作成します。
- **引数**:
    - `conf_file (str)`: キャリブレーション設定が保存されているJSONファイルへのパス。

### `move_angle(deg)`
- **説明**: キャリブレーション値を元に、指定された角度（-90度から90度）にサーボを移動させます。
- **引数**:
    - `deg (float | str)`: 目標角度。`'center'`, `'min'`, `'max'` のような文字列も指定可能です。

### `move_angle_relative(deg_diff)`
- **説明**: 現在の角度から、指定した角度だけ相対的にサーボを動かします。
- **引数**:
    - `deg_diff (float)`: 角度の変化量。

### `get_angle()`
- **説明**: 現在のサーボの角度を取得します。
- **戻り値**: `float` - 現在の角度。

### `load_conf()` / `save_conf()`
- **説明**: 設定ファイルからキャリブレーション値を読み込む、または現在の値を保存します。

---

## class `MultiServo`

複数の `CalibrableServo` インスタンスをまとめて制御するためのクラスです。ロボットアームなど、複数のサーボを協調させて動かす場合に利用します。

### サンプルプログラム

- [sample_03_multi_servo.py](samples/sample_03_multi_servo.py)

### `__init__(pi, pins, first_move=True, ...)`
- **説明**: `MultiServo`のインスタンスを初期化します。
- **引数**:
    - `pins (list[int])`: 制御対象のサーボが接続されているGPIOピンのリスト。
    - `first_move (bool)`: `True`の場合、初期化時に全サーボを中央位置（0度）に移動させます。

### `move_all_angles_sync(target_angles, move_sec=0.2, step_n=40)`
- **説明**: 全てのサーボを、それぞれの目標角度まで指定した時間をかけて滑らかに同期させて動かします。
- **引数**:
    - `target_angles (list)`: 各サーボの目標角度のリスト。`None`を指定するとそのサーボは動きません。
    - `move_sec (float)`: 動作にかける時間（秒）。
    - `step_n (int)`: 動作を分割するステップ数。数値を大きくすると、より滑らかな動きになります。

### `move_all_angles(target_angles)`
- **説明**: 全てのサーボを、それぞれの目標角度まで即座に動かします。
- **引数**:
    - `target_angles (list)`: 各サーボの目標角度のリスト。

### `get_all_angles()`
- **説明**: 全てのサーボの現在の角度を取得します。
- **戻り値**: `list[float]` - 各サーボの角度のリスト。

### `off()`
- **説明**: 管理している全てのサーボをオフにします。

---

## class `ThreadMultiServo`

`MultiServo`の機能をバックグラウンドスレッドで実行するためのインターフェースクラスです。メインの処理をブロックすることなく、複雑なサーボの動作シーケンスを実行できます。

### `__init__(pi, pins, ...)`
- **説明**: `ThreadMultiServo`のインスタンスを初期化し、バックグラウンドでワーカースレッドを開始します。

### `move_all_angles_sync(target_angles, move_sec=None, ...)`
- **説明**: `MultiServo`の同名メソッドと同じ動作を、コマンドとしてキューに追加します。呼び出し元はブロックされません。

### `sleep(sec)`
- **説明**: 指定した時間、コマンドの実行を一時停止するコマンドをキューに追加します。
- **引数**:
    - `sec (float)`: 停止する時間（秒）。

### `cancel_cmds()`
- **説明**: コマンドキューに溜まっている、まだ実行されていない全てのコマンドをキャンセルします。

### `send_cmd(cmd)`
- **説明**: JSON形式のコマンドを直接キューに送信します。
- **引数**:
    - `cmd (dict)`: 実行させたいJSONコマンド。

### `end()`
- **説明**: ワーカースレッドを安全に停止させ、全てのサーボをオフにします。スレッドの終了を待ってからリターンします。

---

## class `StrCmdToJson`

`web-str-api`などで使用される短縮文字列形式のコマンドを、`ThreadMultiServo`が解釈できるJSON形式のコマンドに変換するユーティリティクラスです。

### `cmd_data_list(cmd_line)`
- **説明**: スペース区切りのコマンドライン文字列を、JSONコマンドのリストに変換します。
- **引数**:
    - `cmd_line (str)`: `"mv:c,c sl:1.0 mv:90,90"` のようなコマンド文字列。
- **戻り値**: `list[dict]` - 変換されたJSONコマンドのリスト。

---

## class `ThreadWorker`

`ThreadMultiServo`の内部で使用されるワーカースレッドクラスです。コマンドキューからコマンドを一つずつ取り出し、`MultiServo`インスタンスを介して実行します。利用者がこのクラスを直接操作する必要は通常ありません。
