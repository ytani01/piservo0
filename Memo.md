# ToDo

- [ ] 相対移動: ThredWorker, etc. 
- [ ] ドキュメントの整備
- [ ] テストプログラムの整備


# --- The following is obsoleted ---

## JSON samples
[{"cmd": "move_pulse",   "pulses": [1000, null, 1800, 2000] }, {"cmd":"sleep", "sec": 1.0},  {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 1000] }, {"cmd": "sleep", "sec": 1.0}, {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 2000] }, {"cmd":"sleep", "sec": 1.0},  {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 1000] }, {"cmd": "sleep", "sec": 1.0}, {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 2000] }, {"cmd":"sleep", "sec": 1.0},  {"cmd": "move_pulse",   "pulses": [1000, null, 1800, 1000] }, {"cmd": "sleep", "sec": 1.0}]

{"cmd": "cancel"}


## bipad

### start server
``` bash
uv run piservo0 web-str-api -a -0.5,1,-1,0.5 17 27 22 25 -d
```

### start client
``` bash
uv run piservo0 web-client
```

** forward **
``` text
Nccf Nbff cbfc    fccN ffbN cfbc

Nfbf NfbF NbfF cbfc   fbfN FbfN FfbN cfbc

Nfbf BccF bbfF cbfc   fbfN FccB Ffbb cfbc 

Ncbf Bfbf bfcF Bbfc cbfc   fbcN fbfB Fcfb cfbB cfbc 
```

** back **
``` text
fbfN cbfc Nfbf cfbc   fbfN cbfc Nfbf cfbc
```
