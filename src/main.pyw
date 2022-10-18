import sys  # sys нужен для передачи argv в QApplication
import logging
import os
import json

import eel

# from PyQt5 import QtWidgets

from itf_handler import ItfHandler
from core.context import Context
from core.fabric import enumerate_entities, get_class_from_imported_module, enitity_fabric
from core.logs.log import init_log
from core.utils import get_comports_list

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

def init_devices():
    if not getattr(context, 'devices'):
        context.devices = []

    else:
        for device in context.devices:
            if device['enabled']:
                device['instance'] = enitity_fabric(context.devices_classes, 'dev_name', device['dev_name'])

def init_comports():
    context.comports = get_comports_list()


def main():
    init_context()
    # init log, get connectiond and devices classes, put them to context
    init_log()
    connections_path = 'src.core.connections'
    if context.run_mode == 'testing':
        connections_path = 'tests.mocks.core.connections'
    init_entities(connections_path, 'connection_type', 'connections_classes')
    init_entities('src.devices', 'dev_name', 'devices_classes')

    # create enabled devices instances
    init_devices()

    init_comports()

    eel.init('src/front', allowed_extensions=['.js', '.html'],)
    eel.start(
        'templates/main.html',
        jinja_templates='templates',
        mode='chrome',
        size=(720, 480),
        position=(0,0)
    )

    # app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    # # Создаём объект класса ItfHandler
    # window = ItfHandler()

    # window.show()  # Показываем окно
    # app.exec_()    # и запускаем приложение

if __name__ == "__main__":
    main()