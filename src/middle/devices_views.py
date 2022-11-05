import eel

from core.fabric import add_device
from core.utils import get_devices_list, get_devices_models_list, get_devices_labels_list


@eel.expose
def e_get_devices_models_list(group=None):
    return get_devices_models_list(group)

@eel.expose
def e_get_devices_labels_list():
    return get_devices_labels_list()

@eel.expose
def e_get_added_devices():
    return get_devices_list()

@eel.expose
def e_add_new_device(device_name, device_type, device_model, device_connection_type, device_addr):
    if device_name is None or device_name == '':
        return {'status': 'fail', 'message': 'Не указана метка прибора'}
    if device_type is None or device_type == '':
        return {'status': 'fail', 'message': 'Не указан тип прибора'}
    if device_model is None or device_model == '':
        return {'status': 'fail', 'message': 'Не указана модель прибора'}
    if device_connection_type is None or device_connection_type == '':
        return {'status': 'fail', 'message': 'Не указана тип подключения к прибору'}
    if device_addr is None or device_addr == '':
        return {'status': 'fail', 'message': 'Не указан адрес/порт прибора'}

    connection_type = 'socket' if device_connection_type == 'Ethernet' else device_connection_type.lower()

    try:
        add_device(device_name, device_type, device_model, device_connection_type, device_addr)

        return {'status': 'success'}
    except Exception as e:
        print(e)
        return {'status': 'fail', 'message': 'Не удалось добавить прибор'}


