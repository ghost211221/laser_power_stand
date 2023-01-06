import time
import queue
from threading import Thread

import eel

from core.context import Context
from core.queues import TasksQueue
from core.logs.log import LoggingQueue


c = Context()
q = LoggingQueue()
tq = TasksQueue()

def log_processing_worker():
    while not c.exit_mode:
        time.sleep(0.001)
        try:
            data = q.get(timeout=0.1)
            eel.push_el_to_log(data)
        except queue.Empty:
            pass

def task_processing_worker():
    while not c.exit_mode:
        try:
            # get task and create Thread
            data = tq.get(timeout=0.1)
            for device_lab in data[0]:
                device = c.get_device_by_lab(device_lab)
                try:
                    func = getattr(device, data[1])
                    func(data[2])

                except AttributeError:
                    pass

        except queue.Empty:
            pass
        time.sleep(1)

def get_devices_status_worker():
    while not c.exit_mode:
        for device in c.devices:
            eel.set_device_status(device.label, device.status)
        time.sleep(0.5)

