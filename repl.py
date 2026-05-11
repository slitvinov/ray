from multiprocessing.managers import BaseManager
from queue import Queue, Empty
import code, os, socket, itertools, threading, cloudpickle, pathlib, time, re

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
    import ctypes, ctypes.util
    time.sleep(1)
    host = re.sub("[.].*", "", socket.gethostname())
    aff = sorted(os.sched_getaffinity(0))
    if hasattr(os, 'sched_getcpu'):
        cpu = os.sched_getcpu()
    else:
        libc = ctypes.CDLL(ctypes.util.find_library('c') or 'libc.so.6')
        libc.sched_getcpu.restype = ctypes.c_int
        cpu = libc.sched_getcpu()
    return host, os.getpid(), cpu, tuple(aff)

SOCK = os.environ['MANAGER_SOCK_DRIVER']
pathlib.Path(SOCK).unlink(missing_ok=True)
tasks, results = Queue(), Queue()
BaseManager.register('tasks',   callable=lambda: tasks)
BaseManager.register('results', callable=lambda: results)
server = BaseManager(address=SOCK, authkey=b'').get_server()
threading.Thread(target=server.serve_forever, daemon=True).start()
counter = itertools.count()
code.interact(local={'pmap': pmap, 'cpu_info': cpu_info})
