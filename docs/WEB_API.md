# Web APIによるサーボ制御

`piservo0`は、文字列コマンドをHTTP経由で送信するためのWeb APIサーバーとクライアントを提供する。これにより、ネットワーク経由でリモートからサーボを制御できる。

## 概要

Web APIサーバーは、FastAPIをベースにしており、HTTPリクエストを受け取って文字列コマンドを実行する。Web APIクライアントは、このサーバーに対してHTTPリクエストを送信し、サーボの制御を行う。

## サーバーの起動 (`uv run piservo0 web-str-api`)

まず、サーボが接続されているRaspberry PiなどのデバイスでWeb APIサーバーを起動する。

```bash
uv run piservo0 web-str-api --pins "17,27,22,25" --angle-factor "-1,-1,1,1"
```

*   `--pins`: 制御するGPIOピンのリストをカンマ区切りで指定する。
*   `--angle-factor`: 各サーボの角度係数をカンマ区切りで指定する。サーボの回転方向を調整するために使用する。
*   `--server_host` (`-s`): サーバーがリッスンするホスト名またはIPアドレス（デフォルト: `0.0.0.0`）。
*   `--port` (`-p`): サーバーがリッスンするポート番号（デフォルト: `8000`）。

### サーバー起動時の出力例

```
INFO:     Will watch for changes in these directories: ['/home/ytani/work/piservo0']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
Initializing ...
INFO:     Application startup complete.
```

## クライアントからのコマンド送信 (`uv run piservo0 web-client`)

サーバーが起動したら、別のターミナルからWebクライアントを使用してコマンドを送信できる。

### 1. 単一コマンドの送信

コマンドライン引数として直接コマンドを渡す。

```bash
uv run piservo0 web-client fbcb
```

### 2. 複数のコマンドをシーケンスとして送信

複数のコマンドをスペースで区切って渡す。

```bash
uv run piservo0 web-client "fbcb 0.5 bcfb 0.5"
```

### 3. 対話モード

コマンドライン引数を指定しない場合、対話モードで起動し、プロンプトからコマンドを入力できる。

```bash
uv run piservo0 web-client
```

プロンプトが表示されたら、コマンドを入力してEnterキーを押す。`Ctrl-C`または`Ctrl-D`で終了する。

**対話モードでの操作例:**

```
localhost:8000> {"Hello": "World"}
* history file: /home/user/.piservo0_webclient_history
* Ctrl-C (Interrput) or Ctrl-D (EOF) for quit
> fbcb
localhost:8000> [{"cmd": "move_angle_sync", "target_angles": [-35, -35, 35, 35], "move_sec": null, "step_n": null}]
> 0.5
localhost:8000> [{"cmd": "sleep", "sec": 0.5}]
> bcfb 0.5 fbcb
localhost:8000> [{"cmd": "move_angle_sync", "target_angles": [35, -35, -35, 35], "move_sec": null, "step_n": null}, {"cmd": "sleep", "sec": 0.5}, {"cmd": "move_angle_sync", "target_angles": [-35, -35, 35, 35], "move_sec": null, "step_n": null}]
> z
localhost:8000> [{"cmd": "cancel"}]
> .
localhost:8000> [{"cmd": "move_angle_sync", "target_angles": [null, null, null, null], "move_sec": null, "step_n": null}]
> ^C
* Bye
```

### クライアントオプション

*   `--server_host` (`-s`): 接続するサーバーのホスト名またはIPアドレス（デフォルト: `localhost`）。
*   `--port` (`-p`): 接続するサーバーのポート番号（デフォルト: `8000`）。
