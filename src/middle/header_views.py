import os
import json

import eel

@eel.expose
def save_config(file_name, devices):
    if not file_name:
        return
    
    with open(os.path.join('configs', file_name), 'w') as f:
        f.write(json.dumps(devices))

@eel.expose
def get_configs():
    if os.path.exists('configs'):
        return [fn.replace('.json', '') for fn in os.listdir('configs')]
    return []

@eel.expose
def get_config(conf_name):
    if not conf_name:
        return {'error': True}
    
    file_name = os.path.join('configs', conf_name)
    if not os.path.exists(file_name):
        return {'error': True}
    
    return json.load(file_name)
                          