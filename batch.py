import threading
import cloudpickle
from pathlib import Path
from multiprocessing.managers import BaseManager
from queue import Queue, Empty

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

N = len(open('hosts').read().split())
args = list(range(20))
pending = set(range(len(args)))
out = {}

def submit(ids):
    for i in ids:
        tasks.put((i, cloudpickle.dumps((work, (args[i],)))))

submit(pending)
while pending:
    try:
        i, r = results.get(timeout=5)
    except Empty:
        submit(list(pending))
        continue
    if i in pending:
        pending.remove(i)
        out[i] = r

for _ in range(N):
    tasks.put(None)

for i in range(len(args)):
    print(out[i])
