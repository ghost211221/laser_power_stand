import serial.tools.list_ports

def get_comports_list():
    return [port.name for port in serial.tools.list_ports.comports()]
