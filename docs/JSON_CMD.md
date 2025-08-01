# JSON Commands for `web-json-api`

## e.g.

**同期移動**
``` json
{
  "cmd": "move_angle_sync",
  "angles": [0, null, 30, -60],
  "move_sec": 0.2,
}
```

**sleep**
``` json
{
  "cmd": "sleep",
  "sec": 0.5
}
```

**move sec: estimated move time**
``` json
{
  "cmd": "move_sec",
  "sec": 0.2
}
```

**step count**
``` json
{
  "cmd": "step_n",
  "n": 30
}
```

**interval**
``` json
{
  "cmd": "interval",
  "sec": 0.5
}
```

**move to pulse**
``` json
{
  "cmd": "move_pulse",
  "pulses": [1000, null, 1500, 2000]
}
```
