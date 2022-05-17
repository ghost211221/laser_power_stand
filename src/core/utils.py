import serial.tools.list_ports

def get_comports_list():
    return serial.tools.list_ports.comports() or []
