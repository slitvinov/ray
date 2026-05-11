import os
import cloudpickle
from multiprocessing.managers import BaseManager

BaseManager.register('tasks')
BaseManager.register('results')

m = BaseManager(address=os.environ['MANAGER_SOCK'], authkey=b'')

try:
    m.connect()
    tasks, results = m.tasks(), m.results()
    while True:
        item = tasks.get()
        if item is None:
            break
        i, blob = item
        fn, args = cloudpickle.loads(blob)
        try:
            results.put((i, fn(*args)))
        except Exception as e:
            results.put((i, e))
except (EOFError, ConnectionResetError, BrokenPipeError):
    pass
