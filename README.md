# cowork

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/slitvinov/ray/HEAD?labpath=cowork.ipynb)

Distributed Python over plain SSH using `cloudpickle`.

- `worker.py` — connects to manager via Unix socket, runs `(fn, args)` tasks.
- `batch.py` — driver that submits squaring tasks and prints results.
- `repl.py` — REPL exposing `pmap`.
- `run.sh` — spawns SSH workers (one per line of `hosts`) then runs the script.
- `hosts` — one host per line.
- `apt.txt`, `requirements.txt` — Binder env: `openssh-server` + `cloudpickle`, `jupytext`.

Binder rebuilds on first launch after each push to `HEAD`. Replace `HEAD` in the badge URL to pin a tag/branch/commit.

```
$ sh run.sh batch.py
       hal          0
    glados          1
       hal          4
       hal         16
    glados          9
       hal         36
    glados         25
       hal         49
    glados         64
       hal         81
```

Results print as they arrive, so order depends on which worker finishes first — not input order.

REPL

```
$ sh run.sh repl.py
Python 3.14.4 (main, ...) [...]
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> import socket, statistics, time
>>> def f(x): return f"{socket.gethostname().split('.')[0]} got {x}"
>>> pmap(f, range(4))
['hal got 0', 'glados got 1', 'hal got 2', 'glados got 3']
>>> pmap(lambda x: statistics.mean(x), [[1, 3], [10, 30]])
[2, 20]
>>> pmap(lambda x: 1 / x, [-1, 0, 1])
[-1.0, ZeroDivisionError('division by zero'), 1.0]
>>> def slow(x): time.sleep(5); return x
>>> t=time.time(); pmap(slow, range(4)); print(f"{time.time()-t:.2f}s")
[0, 1, 2, 3]
10.37s
>>> ^D
now exiting InteractiveConsole...
```
