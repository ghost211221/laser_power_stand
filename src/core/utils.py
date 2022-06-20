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

def get_pm_devices():
    return [dev_dict['instance'] for dev_dict in context.devices if dev_dict['type'] == 'power_meter']
