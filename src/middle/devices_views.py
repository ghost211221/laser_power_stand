import eel

from core.consts import CONNECTIONS_TYPES
from core.context import Context
from core.exceptions import ConnectionError
from core.fabric import add_device
from core.utils import get_devices_list, get_devices_models_list, get_devices_labels_list, get_device_by_label
from core.queues import TasksQueue


context = Context()
tq = TasksQueue()


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

    connection_type = None
    for tup in CONNECTIONS_TYPES:
        if device_connection_type in tup:
            connection_type = tup[0]

    if not connection_type:
        return {'status': 'fail', 'message': 'Неизвестный тип подключения: {device_connection_type}'}

    try:
        add_device(device_name, device_type, device_model, connection_type, device_addr)

        return {'status': 'success'}
    except Exception as e:
        print(e)
        return {'status': 'fail', 'message': 'Не удалось добавить прибор'}


@eel.expose
def e_get_device_info(device_name):
    """Get info of device by its label"""
    device = get_device_by_label(device_name)

    if not device:
        return {'status': 'fail', 'message': f'Не найден прибор с меткой {device_name}'}

    return {
        'status': 'success',
        'device_name': device.label,
        'device_type': device.dev_type,
        'device_model': device.dev_name,
        'device_connection_type': device.connection_type,
        'device_addr': device.dev_addr,
        'device_status': device.status
    }

@eel.expose
def e_get_connections_translations():
    return CONNECTIONS_TYPES

@eel.expose
def e_update_device(label, connection_type, addr):
    """change device settings"""
    device = get_device_by_label(label)
    if not device:
        return {'status': 'fail', 'message': f'Не найден прибор с меткой {label}'}

    # if connected - disconnect
    reconnect = bool(device.connection)
    if reconnect:
        device.close()
    device.set_connection(connection_type)
    device.set_addr(addr)
    if reconnect:
        device.connect()

    return {
        'status': 'success'
    }

@eel.expose
def e_connect_device(dev_name, mode='connect'):
    msg = ''
    status = 'success'
    try:
        if mode == 'connect':
            tq.put(([dev_name,], 'connect', []))
            tq.put(([dev_name,], 'init', []))
        elif mode == 'disconnect':
            tq.put(([dev_name,], 'close', []))
        else:
            status = 'fail'
            msg = f'Недопустимая операция: {mode}'
    except ConnectionError as e:
        msg = e
        status = 'fail'

    return {'status': status, 'message': msg}

@eel.expose
def e_delete_device(dev_name):
    msg = ''
    status = 'success'
    try:
        for device in context.devices:
            if dev_name == device.label:
                del context.devices[context.devices.index(device)]
    except Exception as e:
        msg = f'Не удалось удалить прибор: {e}'
        status = 'fail'

    return {'status': status, 'message': msg}
