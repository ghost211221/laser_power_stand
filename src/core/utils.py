from serial.tools import list_ports

def get_comports_list():
    return list_ports.comports() or []

