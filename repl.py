from multiprocessing.managers import BaseManager
from queue import Queue, Empty
import code, os, socket, itertools, threading, cloudpickle, pathlib


SOCK = '/tmp/m.sock'
pathlib.Path(SOCK).unlink(missing_ok=True)

tasks, results = Queue(), Queue()
BaseManager.register('tasks',   callable=lambda: tasks)
BaseManager.register('results', callable=lambda: results)
server = BaseManager(address=SOCK, authkey=b'').get_server()
threading.Thread(target=server.serve_forever, daemon=True).start()

counter = itertools.count()

def gather(ids, blobs, timeout):
    pending = dict(zip(ids, blobs))
    for i, blob in pending.items():
        tasks.put((i, blob))
    out = {}
    while pending:
        try:
            i, r = results.get(timeout=timeout)
        except Empty:
            for i, blob in pending.items():
                tasks.put((i, blob))
            continue
        if i in pending:
            del pending[i]
            out[i] = r
    return [out[i] for i in ids]

def pmap(fn, xs, timeout=None):
    xs = list(xs)
    ids = [next(counter) for _ in xs]
    blobs = [cloudpickle.dumps((fn, (x,))) for x in xs]
    return gather(ids, blobs, timeout)

def cpu_info(_=None):
    aff = sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
    return socket.gethostname(), os.getpid(), aff

code.interact(local={'pmap': pmap, 'cpu_info': cpu_info})
