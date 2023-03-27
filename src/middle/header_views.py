import os
import json

import eel

from src.core.consts import CONNECTIONS_TYPES
from src.core.context import Context
from src.core.fabric import add_device


context = Context()


@eel.expose
def save_config(file_name, devices):
    if not file_name:
        return
    
    with open(os.path.join('configs', file_name), 'w') as f:
        f.write(json.dumps(devices))

@eel.expose
def get_configs():
    if os.path.exists('configs'):
        return {'error': False, 'data': [fn.replace('.json', '') for fn in os.listdir('configs')]}
    return {'error': False, 'data': []}

@eel.expose
def load_config(conf_name):
    if not conf_name:
        return {'error': True, 'msg': 'Не указано имя конфигурации'}
    
    file_name = os.path.join('configs', conf_name)
    if not os.path.exists(file_name):
        return {'error': True, 'msg': 'Указанная конфигурация не существует'}
    
    with open(file_name) as fp:
        devices = json.load(fp)
        for device in devices:
            connection_type = None
            for tup in CONNECTIONS_TYPES:
                if device['connection_type'] in tup:
                    connection_type = tup[0]
                    break

            if not connection_type:
                return {'status': 'fail', 'message': f'Неизвестный тип подключения: {device["connection_type"]}'}
            
            try:
                dev = add_device(device['label'], device['type'], device['model'], connection_type, device['addr'])
                for analysis in context.analyses:
                    analysis.add_device_traces(dev)
                return {'status': 'success'}
            except Exception as e:
                print(e)
                return {'status': 'fail', 'message': 'Не удалось добавить прибор'}
        