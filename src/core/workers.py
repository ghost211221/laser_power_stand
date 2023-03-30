import time
import queue
from threading import Thread

import eel

from .context import Context
from .queues import TasksQueue
from .logs.log import LoggingQueue
from .utils import get_device_by_statuses_and_type, get_callback


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
    def _get_callback_from_args(args):
        for i, arg in enumerate(args):
            if i > 0 and args[i-1] == 'callback':
                return arg
            
    def _get_callback_args(args):
        for i, arg in enumerate(args):
            if i >= 3 and args[i-3] == 'callback' and args[i-1] == 'analyse':
                return [('analyse', arg), ]
            
        return []
            
    def _get_func_args(args):
        for i, arg in enumerate(args):
            if i >= 1 and args[i-1] == 'value':
                return [arg, ]
            
        return []
            
    while not c.exit_mode:
        try:
            # get task and create Thread``
            priority, data = tq.get(timeout=0.1)
            for device_lab in data[0]:
                device = c.get_device_by_lab(device_lab)
                try:
                    func = getattr(device, data[1])
                    func_args = _get_func_args(data[2])
                    res = func(*func_args)
                    args = data[2]
                    cb = _get_callback_from_args(args)
                    if cb:
                        callback = get_callback(cb)
                        args = _get_callback_args(args)
                        if callback:
                            callback(res, device, *args)

                except AttributeError as e:
                    print(e)

        except queue.Empty:
            pass
        time.sleep(1)

def get_devices_status_worker():
    while not c.exit_mode:
        for device in c.devices:
            eel.set_device_status(device.label, device.status)
        time.sleep(0.5)

def get_laser_temperature():
    while not c.exit_mode:
        dev = get_device_by_statuses_and_type(('processing', 'ready'), 'laser')
        if dev:
            try:
                tq.put(([dev.label, ], 'get_temperature', ['callback', 'show_temp']), priority=0)
                # val, msg = dev.get_temperature()
                # eel.show_temp(val, msg)
            except Exception as e:
                q.put('Error During temp meas')
                q.put(e)
                eel.show_temp('', '')
        else:
            eel.show_temp('', '')

        time.sleep(5)

