# cowork

Distributed Python over plain SSH using `cloudpickle`.

- `worker.py` — connects to manager via Unix socket, runs `(fn, args)` tasks.
- `batch.py` — driver that submits 20 squaring tasks and prints results.
- `repl.py` — interactive REPL exposing `submit`, `pmap`.
- `run.sh` — spawns SSH workers (one per line of `hosts`) then runs the script.
- `hosts` — one host per line.

```
$ sh run.sh batch.py
       hal          0
    glados          1
       hal          4
    glados          9
       hal         16
       ...
       hal        324
    glados        361
```

REPL

```
$ sh run.sh repl.py
Python 3.14.4 (main, ...) [...]
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> def f(x): import socket; return f"{socket.gethostname().split('.')[0]} got {x}"
>>> submit(f, 42)
'hal got 42'
>>> pmap(f, range(4))
['hal got 0', 'glados got 1', 'hal got 2', 'glados got 3']
>>> pmap(lambda x: x*x, range(10))
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
>>> def slow(x): import time; time.sleep(2); return x
>>> import time; t=time.time(); pmap(slow, range(4)); print(f"{time.time()-t:.2f}s")
[0, 1, 2, 3]
4.04s
>>> ^D
$
```
