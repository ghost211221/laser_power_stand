import math

import serial.tools.list_ports

from core.context import Context

context = Context()

def get_comports_list():
    return [port.name for port in serial.tools.list_ports.comports()]

def mW_to_dBm(mW):
    return 10 * math.log10(mW)

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
            'connected': bool(device.connection)
        })

    return devices

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
