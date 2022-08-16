from serial import Serial

from ..abstract import AbstractConnection

# TODO: add log
# TODO: add exceptions handling

class Com(AbstractConnection):
    connection_type = 'com'

    def __init__(self, comport, timeout=1, baudrate=9600):
        self.__comport = comport
        self.__port = None
        self.__timeout = timeout
        self.__baudrate = baudrate

    def connect(self):
        self.__port = Serial()
        self.__port.port = self.__comport
        self.__port.baudrate = self.__baudrate
        self.__port.timeout = self.__timeout
        self.__port.open()
        self.connected = True

    def close(self):
        self.__port.close()
        self.__port = None
        self.connected = False

    def send(self, data):
        self.__port.write(data)

    def read(self, data):
        try:
            line = self.__port.readline()

            return line
        except TimeoutError as e:
            pass

    def io(self, data):
        self.__port.write(data)
        try:
            line = self.__port.readline()

            return line
        except TimeoutError as e:
            pass
