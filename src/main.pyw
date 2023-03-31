import sys  # sys нужен для передачи argv в QApplication
import logging
import os
import json
from threading import Thread

import eel

from  middle.devices_views import *
from  middle.analyses_views import *
from  middle.log_views import *
from  middle.header_views import *

from analyzes.single_meas import SingleMeas
from analyzes.cont_meas import ContMeas
from analyzes.scan_meas import ScanMeas
from core.context import Context
from core.fabric import enumerate_entities, get_class_from_imported_module
from core.logs.log import init_log
from core.workers import log_processing_worker, task_processing_worker, get_devices_status_worker, get_laser_temperature


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
    context.exit_mode = True
    exit()

def prepare_dirs():
    if not os.path.exists('./configs'):
        os.mkdir('./configs')

    if not os.path.exists('./traces'):
        os.mkdir('./traces')

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

    prepare_dirs()

    eel.init('src/front', allowed_extensions=['.js', '.html'],)

    log_queue_processor = Thread(target=log_processing_worker)
    log_queue_processor.start()

    tasks_processor = Thread(target=task_processing_worker)
    tasks_processor.start()

    temp_processor = Thread(target=get_laser_temperature)
    # temp_processor.start()

    # status_processor = Thread(target=get_devices_status_worker)
    # status_processor.start()

    eel.start(
        'templates/main.html',
        jinja_templates='templates',
        mode='chrome',
        size=(1160, 975),
        position=(0,0),
        jinja_env={'hello': 'hello'},
        close_callback=close_callback
    )

if __name__ == "__main__":
    main()