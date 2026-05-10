import os
import time
import cloudpickle
from multiprocessing.managers import BaseManager

BaseManager.register('tasks')
BaseManager.register('results')

m = BaseManager(address=os.environ['MANAGER_SOCK'], authkey=b'')
for _ in range(50):
    try:
        m.connect()
        break
    except (FileNotFoundError, ConnectionRefusedError, ConnectionResetError, EOFError, BrokenPipeError):
        time.sleep(0.1)
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
