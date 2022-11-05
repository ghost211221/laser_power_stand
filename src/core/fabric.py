import importlib
import os

from core.context import Context

context = Context()

def enumerate_entities(path: str):
    """ enumerate modules in path, excluding abstract.py and __init__.py
    -- path - path like src.core.utils
    """
    modules = []
    try:
        path_ = path.replace('.', '/')
        dirs = [name for name in os.listdir(path_) if os.path.isdir(os.path.join(path_, name))]


        for dir_name in dirs:
            if '__' in dir_name:
                continue

            path_ = '.'.join(path.split('.')[0:])
            modules.append(importlib.import_module(f'{path_}.{dir_name}.{dir_name}'))
    except ModuleNotFoundError:
        if 'connections' in path:
            import core.connections.com.com as Com
            import core.connections.socket.socket as Socket
            import core.connections.visa.visa as Visa

            modules = [Com, Socket, Visa]

        elif 'devices' in path:
            import devices.itla5300.itla5300 as ITLA5300
            import devices.pm2100.pm2100 as PM2100

            modules = [ITLA5300, PM2100]

        else:
            raise Exception(f'Unknown path: {path}')
    return modules

def get_class_from_imported_module(module):
    name = module.__name__
    for attr in dir(module):
        if attr.lower() in name and name != attr.lower():
            return getattr(module, attr)

def enitity_fabric(classes_dict, field_name, field_value):
    for class_ in classes_dict.values():
        if getattr(class_, field_name) == field_value:
            return class_()

def add_device(device_name, device_type, device_model, device_connection_type, device_addr):
    """Add new device object"""
    for k, v in context.devices_classes.items():
        if k == device_model:
            device = v(device_name)
            device.set_connection(device_connection_type)
            device.set_addr(device_addr)
            context.devices.append(device)