import threading
import cloudpickle
from pathlib import Path
from multiprocessing.managers import BaseManager
from queue import Queue, Empty

def work(x):
    import socket
    host = socket.gethostname().split('.')[0]
    return f"{host:>10s} {x * x:>10d}"

def submit(ids):
    for i in ids:
        tasks.put((i, cloudpickle.dumps((work, (args[i],)))))

SOCK = '/tmp/m.sock'
Path(SOCK).unlink(missing_ok=True)
tasks, results = Queue(), Queue()
BaseManager.register('tasks',   callable=lambda: tasks)
BaseManager.register('results', callable=lambda: results)
server = BaseManager(address=SOCK, authkey=b'').get_server()
threading.Thread(target=server.serve_forever, daemon=True).start()
N = len(open('hosts').read().split())
args = list(range(10))
pending = set(range(len(args)))
submit(pending)
while pending:
    try:
        i, r = results.get(timeout=60)
    except Empty:
        submit(list(pending))
        continue
    if i in pending:
        pending.remove(i)
        print(r)
for _ in range(N):
    tasks.put(None)
