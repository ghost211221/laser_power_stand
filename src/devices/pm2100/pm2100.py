import os
from copy import copy
import struct
import logging

import yaml

from ..abstract import AbstractDevice
from core.context import Context
from core.logs.log import LoggingQueue
from core.exceptions import ConnectionError

# mock connection module for if have no access to devices
if Context().run_mode == 'testing':
    from tests.mocks.core.connections.socket import Socket
elif Context().run_mode == 'normal':
    from core.connections.socket.socket import Socket
else:
    raise Exception(f'Unkonwn mode "{Context().run_mode}"')


log = logging.getLogger(__name__)


class ITLA5300(AbstractDevice):

    connection_types = ['com']
    dev_name = 'ITLA5300'

    def __init__(self):
        self.baudrate = None
        self.__q = LoggingQueue()

    def set_connection(self, connection_type):
        self.connection_type = connection_type

    def set_addr(self, addr):
        self.dev_addr = addr

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate

    def connect(self):
        self.connection = Socket(self.dev_addr)
        self.connection.connect()
        self.status = 'idle'
        self.__q.put(f'\n{self.dev_name} connected to {self.dev_addr}')

    def close(self):
        self.connection.close()
        self.status = 'init'
        self.__q.put(f'\n{self.dev_name} disconnected from {self.dev_addr}')

    def send(self, data):
        self.connection.send(data)

    def read(self):
        self.connection.read()

    def io(self):
        self.connection.io()
        
    def init(self):
        
        self.status = 'ready'
    