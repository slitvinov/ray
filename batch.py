from multiprocessing.managers import BaseManager
from queue import Queue, Empty
import socket, re, time, threading, cloudpickle, pathlib

def work(x):
    time.sleep(2)
    return socket.gethostname(), x * x

def submit(ids):
    for i in ids:
        tasks.put((i, cloudpickle.dumps((work, (args[i],)))))

SOCK = '/tmp/m.sock'
pathlib.Path(SOCK).unlink(missing_ok=True)
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
        i, (host, ans) = results.get(timeout=60)
    except Empty:
        submit(list(pending))
        continue
    if i in pending:
        pending.remove(i)
        host = re.sub("[.].*", "", host)
        print(f"{host:>20s} {ans:>10d}")
for _ in range(N):
    tasks.put(None)
