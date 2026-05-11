# cowork

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/slitvinov/ray/HEAD?labpath=cowork.ipynb)

Distributed Python over plain SSH using `cloudpickle`.

- `worker.py` — connects to manager via Unix socket, runs `(fn, args)` tasks.
- `batch.py` — driver that submits squaring tasks and prints results.
- `repl.py` — REPL exposing `pmap`.
- `run.sh` — spawns SSH workers (one per line of `hosts`) then runs the script.
- `hosts` — one host per line.
- `apt.txt`, `requirements.txt` — Binder env: `openssh-server` + `cloudpickle`, `jupytext`.

Bootstrap each host in `hosts` with matching Python + `cloudpickle` in `~/miniforge3`:

```
ssh <host> bash <<'!'
OS=$(uname -s); [ "$OS" = Darwin ] && OS=MacOSX
ARCH=$(uname -m)
curl -fsSL "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$OS-$ARCH.sh" -o /tmp/mf.sh
bash /tmp/mf.sh -b
rm /tmp/mf.sh
~/miniforge3/bin/conda install -y python=3.14
~/miniforge3/bin/pip install cloudpickle
!
```

```
$ echo 'rc\nhal\nglados\nrc\nlocalhost' > hosts
$ sh run.sh batch.py
		 mac          0
		 mac          1
		 mac          4
	      glados          9
		 hal         16
	 holylogin07         25
	 holylogin07         36
		 mac         49
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

Slurm (FAS RC, driven from a laptop)

Add a `Host holy*` block to `~/.ssh/config` so compute nodes are reachable through the login alias `rc`:

```
Host holy*
    User <user>
    ProxyJump rc
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
```

Submit a holding job (4 nodes × 4 workers each = 16):

```
JOB=$(ssh rc 'sbatch --parsable -J cowork -N 4 -c 4 -t 10:00 -p shared --mem=4G --wrap="sleep infinity"')
```

Expand the node list into `hosts`:

```
ssh rc "scontrol show hostnames \$(squeue -j $JOB -h -o %N) | awk '{for(i=0;i<4;i++) print}'" > hosts
```

Run:

```
sh run.sh repl.py
```

```
>>> import time
>>> def slow(x): time.sleep(10); return x
>>> t=time.time(); pmap(slow, range(160)); print(f"{time.time()-t:.2f}s")
[0, 1, ..., 159]
103.82s
```

160 × 10 s = 1600 s sequential; ~100 s ideal on 16 workers — near-perfect scaling.

Check that workers land on distinct cores:

```
>>> import pprint; pprint.pprint(set(pmap(cpu_info, range(32))))
{('holy7c06107', 3555778, (0, 1, 2, 3)),
 ('holy7c06107', 3555779, (0, 1, 2, 3)),
 ('holy7c06107', 3555793, (0, 1, 2, 3)),
 ('holy7c06107', 3555815, (0, 1, 2, 3)),
 ('holy7c06109', 4069370, (20, 21, 22, 23)),
 ('holy7c06109', 4069371, (20, 21, 22, 23)),
 ('holy7c06109', 4069431, (20, 21, 22, 23)),
 ('holy7c06109', 4069432, (20, 21, 22, 23)),
 ('holy7c06204', 39241, (41, 42, 43, 44)),
 ('holy7c06204', 39285, (41, 42, 43, 44)),
 ('holy7c06204', 39313, (41, 42, 43, 44)),
 ('holy7c06204', 39384, (41, 42, 43, 44)),
 ('holy7c08102', 4096915, (2, 3, 8, 9)),
 ('holy7c08102', 4096943, (2, 3, 8, 9)),
 ('holy7c08102', 4096967, (2, 3, 8, 9)),
 ('holy7c08102', 4096981, (2, 3, 8, 9))}
```

Release the allocation when done:

```
ssh rc scancel $JOB
```
