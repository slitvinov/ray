# ---
# jupyter:
#   jupytext:
#     comment_magics: false
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% language="sh"
# mkdir -p ~/sshd
# test -f ~/sshd/host_key || ssh-keygen -t ed25519 -N '' -f ~/sshd/host_key -q
# test -f ~/.ssh/id_ed25519 || ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519 -q
# cp ~/.ssh/id_ed25519.pub ~/.ssh/authorized_keys
# chmod 600 ~/.ssh/id_ed25519 ~/.ssh/authorized_keys
# pkill -x sshd 2>/dev/null
# sleep 0.2
# /usr/sbin/sshd -p 2222 -h ~/sshd/host_key \
#     -o PidFile=/tmp/sshd.pid \
#     -o UsePAM=no

# %%
%%writefile /home/jovyan/.ssh/config
Host local
    HostName localhost
    Port 2222
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR

# %%
%%writefile hosts
local
local

# %%
%%writefile worker.py
import os
import cloudpickle
from multiprocessing.managers import BaseManager

BaseManager.register('tasks')
BaseManager.register('results')

m = BaseManager(address=os.environ['MANAGER_SOCK'], authkey=b'')
m.connect()
tasks, results = m.tasks(), m.results()

try:
    while True:
        blob = tasks.get()
        fn, args = cloudpickle.loads(blob)
        try:
            results.put(fn(*args))
        except Exception as e:
            results.put(e)
except (EOFError, ConnectionResetError, BrokenPipeError):
    pass

# %%
%%writefile batch.py
import threading
import cloudpickle
from pathlib import Path
from multiprocessing.managers import BaseManager
from queue import Queue

SOCK = '/tmp/m.sock'
Path(SOCK).unlink(missing_ok=True)

def work(x):
    import socket
    host = socket.gethostname().split('.')[0]
    return f"{host:>10s} {x * x:>10d}"

tasks, results = Queue(), Queue()
BaseManager.register('tasks',   callable=lambda: tasks)
BaseManager.register('results', callable=lambda: results)
server = BaseManager(address=SOCK, authkey=b'').get_server()
threading.Thread(target=server.serve_forever, daemon=True).start()

for x in range(20):
    tasks.put(cloudpickle.dumps((work, (x,))))
for _ in range(20):
    print(results.get())

# %% language="sh"
# (
#     rm -f /tmp/m-*.sock /tmp/m.sock
#     while ! test -S /tmp/m.sock; do sleep 0.05; done
#     i=0
#     while IFS= read -r host; do
#         sock=/tmp/m-$i.sock
#         ssh -R "$sock:/tmp/m.sock" \
#             -o StreamLocalBindUnlink=yes \
#             -o ExitOnForwardFailure=yes \
#             -o LogLevel=QUIET \
#             "$host" 'MANAGER_SOCK=$sock /srv/conda/envs/notebook/bin/python3 -' < worker.py &
#         i=$((i + 1))
#     done < hosts
#     wait
# ) &
#
# python3 batch.py
