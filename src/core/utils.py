import math

import serial.tools.list_ports

import eel

import src.core.callbacks as cb
from src.core.context import Context


context = Context()

def get_callback(cb_name):
    """get callback by name, return None if not found"""
    return getattr(cb, cb_name, None)

def get_comports_list():
    return [port.name for port in serial.tools.list_ports.comports()]

def mW_to_dBm(mW):
    return 10 * math.log10(float(mW))

def dBm_to_mW(dBm):
    return 10 ** (dBm / 10)

def get_devices_list():
    devices = []

    for device in context.devices:
        devices.append({
            'label': device.label,
            'type': device.dev_type,
            'model': device.dev_name,
            'connection_type': device.connection_type,
            'addr': device.dev_addr,
            'status': device.status,
            'connected': bool(device.connection),
            'chanels': device.chanels
        })

    return devices

def get_device_by_statuses_and_type(statuses, dev_type):
    for device in context.devices:
        if device.status in statuses and device.dev_type == dev_type:
            return device

def get_devices_models_list(group=None):
    """get list of devices models. if group proveided - devices of group"""
    devices = []
    for k, v in context.devices_classes.items():
        if not group or v.dev_type == group:
            devices.append(k)

    return devices


def get_devices_labels_list():
    """get list of devices labels."""
    labels = []
    for device in context.devices:
        if device.label:
            labels.append(device.label)

    return labels

def get_device_by_label(label):
    if not label:
        return

    for device in context.devices:
        if device.label == label:
            return device

def get_analyses():
    return context.analyses

def plot_traces(analysis_type, traces):
    data = [
    ]
    for trace in traces:
        temp = dict(sorted(trace.get('data', {}).items()))
        data.append(
            {
                'id': trace.get('id'),
                'title': trace.get('title'),
                'x': list(temp.keys()),
                'y': list(temp.values())
            }
        )
    eel.show_traces(analysis_type, data)
