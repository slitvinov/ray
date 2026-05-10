import code
import threading
import cloudpickle
from pathlib import Path
from multiprocessing.managers import BaseManager
from queue import Queue

SOCK = '/tmp/m.sock'
Path(SOCK).unlink(missing_ok=True)

tasks, results = Queue(), Queue()
BaseManager.register('tasks',   callable=lambda: tasks)
BaseManager.register('results', callable=lambda: results)
server = BaseManager(address=SOCK, authkey=b'').get_server()
threading.Thread(target=server.serve_forever, daemon=True).start()

def submit(fn, *args):
    tasks.put(cloudpickle.dumps((fn, args)))
    return results.get()

def bcast(fn, n, *args):
    blob = cloudpickle.dumps((fn, args))
    for _ in range(n):
        tasks.put(blob)
    return [results.get() for _ in range(n)]

def pmap(fn, xs):
    for x in xs:
        tasks.put(cloudpickle.dumps((fn, (x,))))
    return [results.get() for _ in xs]

code.interact(local={'submit': submit, 'bcast': bcast, 'pmap': pmap})
