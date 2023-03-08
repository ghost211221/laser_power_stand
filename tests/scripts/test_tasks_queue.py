import sys  # sys нужен для передачи argv в QApplication
import logging
import os
import json
from threading import Thread

from src.analyzes.single_meas import SingleMeas
from src.analyzes.cont_meas import ContMeas
from src.analyzes.scan_meas import ScanMeas
from src.core.context import Context
from src.core.fabric import add_device, enumerate_entities, get_class_from_imported_module
from src.core.logs.log import init_log
from src.core.workers import log_processing_worker, task_processing_worker, get_devices_status_worker, get_laser_temperature
from src.core.queues import TasksQueue


tq = TasksQueue()

context = Context()
log = logging.getLogger(__name__)

def init_context():
    if os.path.exists('src/config.json'):
        with open('src/config.json') as f:
            data = json.loads(f.read())

        for k, v in data.items():
            setattr(context, k, v)

def init_entities(path, field, group):
    entities_modules = enumerate_entities(path)
    entities = {}
    for module in entities_modules:
        entity = get_class_from_imported_module(module)
        key = getattr(entity, field)
        entities[key] = entity

    setattr(context, group, entities)

def init_analyses():
    context.analyses.append(SingleMeas())
    context.analyses.append(ContMeas())
    context.analyses.append(ScanMeas())

def close_callback(route, websockets):
    print('callback')
    context.exit_mode = True
    exit()

devices = [
    {
        'device_name': 'l',
        'device_type': 'laser',
        'device_model': 'ITLA5300',
        'connection_type': 'com',
        'device_addr': 'c'
    },
    {
        'device_name': 'm',
        'device_type': 'meter',
        'device_model': 'PM2100',
        'connection_type': 'socket',
        'device_addr': '192.168.1.161:5000'
    }
]



def main():
    init_context()
    # init log, get connectiond and devices classes, put them to context
    init_log()
    connections_path = 'src.core.connections'
    if context.run_mode == 'testing':
        connections_path = 'tests.mocks.core.connections'
    # prepare connection classes
    init_entities(connections_path, 'connection_type', 'connections_classes')
    # prepare devices classes
    init_entities('src.devices', 'dev_name', 'devices_classes')
    init_analyses()

    tasks_processor = Thread(target=task_processing_worker)
    tasks_processor.start()

    print(f'main: {tq}')
    for dev in devices:
        device = add_device(
            device_name=dev.get('device_name'), 
            device_type=dev.get('device_type'), 
            device_model=dev.get('device_model'), 
            device_connection_type=dev.get('connection_type'), 
            device_addr=dev.get('device_addr')
        )
        device.set_connection(dev.get('connection_type'))
        tq.put(([dev.get('device_name'),], 'connect', []))
        tq.put(([dev.get('device_name'),], 'init', []))
    
    an = context.get_analyse_by_name('single_meas')
    an.set_meters([context.get_device_by_lab('m'), ])
    an.set_emitter(context.get_device_by_lab('l'))
    an.add_device_traces(context.get_device_by_lab('m'))

    an.run()
    print(an.traces)
if __name__ == '__main__':
    main()