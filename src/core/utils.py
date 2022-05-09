import importlib
import os

def enumerate_entities(path):
    """ enumerate modules in path, excluding abstract.py and __init__.py
    -- path - path like src.core.utils    
    """
    path_ = path.replace('.', '/')

    files = set(os.listdir(path_))
    modules = []
    for file in files:
        if file.startswith('__') or file == 'abstract.py':
            continue
        modules.append(importlib.import_module('.' + file.replace('.py', ''), path))

    return modules

def get_class_from_imported_module(module):
    name = module.__name__
    for attr in dir(module):
        if name in attr.lower() and name != attr.lower():
            return getattr(module, attr)

def enitity_fabric(classes_list, field_name, field_value):
    for class_ in classes_list:
        if getattr(class_, field_name) == field_value:
            return class_()