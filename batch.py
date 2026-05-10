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
