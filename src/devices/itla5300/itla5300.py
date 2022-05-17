from ..abstract import AbstractDevice

from core.connections.com.com import Com


class ITLA5300(AbstractDevice):

    connection_types = ['com']
    dev_name = 'ITLA5300'

    def __init__(self):
        self.baudrate = None

    def set_connection(self, connection_type):
        self.connection_type = connection_type

    def set_addr(self, addr):
        self.dev_addr = addr

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate

    def connect(self):
        self.connection = Com(self.dev_addr)
        self.connection.connect()

    def send(self, data):
        self.connection.send(data)

    def read(self):
        self.connection.read()

    def io(self):
        self.connection.io()

    