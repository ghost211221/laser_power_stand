import importlib
import os

def enumerate_entities(path: str):
    """ enumerate modules in path, excluding abstract.py and __init__.py
    -- path - path like src.core.utils    
    """
    path_ = path.replace('.', '/')
    dirs = [name for name in os.listdir(path_) if os.path.isdir(os.path.join(path_, name))]
    
    modules = []
    for dir_name in dirs:
        if '__' in dir_name:
            continue
        
        path_ = '.'.join(path.split('.')[1:])
        modules.append(importlib.import_module(f'{path_}.{dir_name}.{dir_name}'))

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