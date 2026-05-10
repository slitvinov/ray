import os
import cloudpickle
from multiprocessing.managers import BaseManager

BaseManager.register('tasks')
BaseManager.register('results')

m = BaseManager(address=os.environ.get('MANAGER_SOCK', '/tmp/m.sock'), authkey=b'')
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
