import time
import queue

import eel

from core.context import Context
from core.logs.log import LoggingQueue


c = Context()
q = LoggingQueue()

def log_processing_worker():
    while not c.exit_mode:
        time.sleep(0.001)
        try:
            data = q.get(timeout=0.1)
            eel.push_el_to_log(data)
        except queue.Empty:
            pass