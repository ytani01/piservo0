# str_to_json

## 書式

def str_to_json(cmdstr: str): -> str

## 機能

コマンド文字列`cmdstr`を以下の例に基づいて、JSON文字列に変換する。

## 基本ルール

- 先頭の2文字は、コマンド種別

- コマンドとパラメータの間の区切り文字は、':'

- ':'以降は、コマンド毎に異なるパラメータ

- コマンド文字列の途中に空白文字は入ってはならない。

- 変換できない場合は、以下を返す。
  '{"err": **元のコマンド文字列**}'

- コマンドの種類は以下の通り
  - 'mv': {"cmd": "move_all_angles_sync"}
  - 'sl': {"cmd": "sleep"}
  - 'ms': {"cmd": "move_sec"}
  - 'st': {"cmd": "step_n"}
  - 'is': {"cmd": "interval"}
  - 'mp': {"cmd": "move_pulse_relative"}
  - 'sc': {"cmd": "set"}  # set center
  - 'sn': {"cmd": "set"}  # set min
  - 'sx': {"cmd": "set"}  # set max
  - 'ca': {"cmd": "cancel"}
  - 'zz': {"cmd": "cancel"}

## 補足ルール

- "angles"の数値は、-90以上、90以下
- "sec"の値は、0以上のfloat
- "n"の値は、1以上のint

## 例

入力: 'mv:40,30,20,10'
出力: '{"cmd": "move_all_angles_sync", "angles": [40,30,20,10]}'

入力: 'mv:-40,.,.'
出力: '{"cmd": "move_all_angles_sync", "angles": [-40,null,null]}'

入力: 'mv:max,min,center'
出力: '{"cmd": "move_all_angles_sync", "angles": ["max","min","center"]}'

入力: 'mv:x,n,c'
出力: '{"cmd": "move_all_angles_sync", "angles": ["max","min","center"]}'

入力: 'mv:x,.,center,20'
出力: '{"cmd": "move_all_angles_sync", "angles": ["max",null,"center",20]}'

入力: 'sl:0.5'
出力: '{"cmd": "sleep", "sec": 0.5}'

入力: 'sl:1'
出力: '{"cmd": "sleep", "sec": 1}'

入力: 'ms:1.5'
出力: '{"cmd": "move_sec", "sec": 1.5}'

入力: 'st:1'
出力: '{"cmd": "step_n", "n": 1}'

入力: 'st:40'
出力: '{"cmd": "step_n", "n": 40}'

入力: 'is:0.5'
出力: '{"cmd": "interval", "sec": 0.5}'

入力: 'mp:2,-20'
出力: '{"cmd": "move_pulse_relative", "servo": 2, "pulse_diff": -20}

入力: 'sc:1'
出力: '{"cmd": "set", "servo": 1, "target": "center"}

入力: 'sn:2'
出力: '{"cmd": "set", "servo": 2, "target": "min"}

入力: 'sx:0'
出力: '{"cmd": "set", "servo": 0, "target": "max"}

入力: 'ca'
出力: '{"cmd": "cancel"}

入力: 'zz'
出力: '{"cmd": "cancel"}
