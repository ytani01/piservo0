# ToDo

-[*] web-json-api: キャンセル機能
-[ ] ドキュメントの整備
-[ ] テストプログラムの整備

# Memo

## JSON samples
[{"cmd": "move_pulse",   "pulses": [1000, null, 1800, 2000] }, {"cmd":"sleep", "sec": 1.0},  {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 1000] }, {"cmd": "sleep", "sec": 1.0}, {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 2000] }, {"cmd":"sleep", "sec": 1.0},  {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 1000] }, {"cmd": "sleep", "sec": 1.0}, {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 2000] }, {"cmd":"sleep", "sec": 1.0},  {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 1000] }, {"cmd": "sleep", "sec": 1.0}]

{"cmd": "cancel"}


## bipad

``` bash
uv run piservo0 web-str-api -a -0.5,1,-1,0.5 17 27 22 25 -d
```


- walk

``` bash
uv run piservo0 web-client
```

``` text
# forward
cccc .5   Nccf Nbff cbfc    fccN ffbN cfbc    cccc

.5 fccN ffbN cfbc Nfbf NfbF NbfF cbfc fbfN FbfN FfbN cfbc Nfbf NfbF NbfF cbfc fbfN FbfN FfbN cfbc Nfbf NfbF NbfF cbfc fbfN FbfN FfbN cfbc

cfbc  Nfbf BccF bbfF cbfc  fbfN FccB Ffbb  cfbc  Nfbf BccF bbfF cbfc  fbfN FccB Ffbb
```

``` text
cccc .5  cfbc .1   Nfbf BccF bbfF cbfc  fbfN FccB Ffbb cfbc    Nfbf BccF bbfF cbfc  fbfN FccB Ffbb cfbc    Nfbf BccF bbfF cbfc  fbfN FccB Ffbb cfbc
```

``` text
# back
cccc  fbfN cbfc Nfbf cfbc  fbfN cbfc Nfbf cfbc
```

``` text
 Ncbf Bfbf bfcF Bbfc cbfc   fbcN fbfB Fcfb cfbB cfbc 
```
