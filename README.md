# cowork

Distributed Python over plain SSH using `cloudpickle` — no Ray, Dask, or MPI.

## Files

- `worker.py` — connects to manager via Unix socket, runs `(fn, args)` tasks.
- `batch.py` — driver that submits 20 squaring tasks and prints results.
- `repl.py` — interactive REPL exposing `submit`, `pmap`.
- `run.sh` — spawns SSH workers (one per line of `hosts`) then runs the script.
- `hosts` — one host per line.

## Setup

On every host in `hosts`, install matching Python + cloudpickle in `~/miniforge3`:

```
ssh hal 'curl -fsSL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh | bash -b && ~/miniforge3/bin/conda install -y python=3.14 && ~/miniforge3/bin/pip install cloudpickle'
```

## Batch run

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

## Interactive REPL

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

`pmap(slow, range(4))` ≈ 4 s, not 8 s — 2 workers run the 4 sleeps in parallel (2 × 2 s).

## How it works

1. `run.sh` waits for `batch.py`/`repl.py` to bind `/tmp/m.sock` (a Unix domain socket via `multiprocessing.managers.BaseManager`).
2. For each host in `hosts`, `ssh -R /tmp/m-N.sock:/tmp/m.sock` reverse-tunnels a fresh socket on the remote back to the driver's socket.
3. The remote `python3 -` reads `worker.py` over SSH stdin (no shared filesystem needed), connects to its local `/tmp/m-N.sock`, pulls cloudpickle blobs from the `tasks` queue, runs them, pushes results.
4. Driver collects results and exits; workers exit on the resulting connection close.
