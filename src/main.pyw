import sys  # sys нужен для передачи argv в QApplication
import logging
import os
import json

import eel

from  middle.devices_views import *

from core.context import Context
from core.fabric import enumerate_entities, get_class_from_imported_module
from core.logs.log import init_log
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

    eel.init('src/front', allowed_extensions=['.js', '.html'],)
    eel.start(
        'templates/main.html',
        jinja_templates='templates',
        mode='chrome',
        size=(1160, 975),
        position=(0,0),
        jinja_env={'hello': 'hello'}
    )

if __name__ == "__main__":
    main()