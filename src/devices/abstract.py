from abc import ABCMeta, abstractmethod
import logging

from core.context import Context
from core.exceptions import ConnectionClassNotFoundError
from core.logs.log import LoggingQueue

log = logging.getLogger(__name__)
context = Context()

class AbstractDevice(metaclass=ABCMeta):
    connection = None
    connection_type = None
    connection_types = []
    dev_name = None
    dev_addr = None
    dev_type = None
    timeout = None
    status = 'init'
    
    def __init__(self):
        self.q = LoggingQueue()

    def set_connection(self, connection_type):
        self.connection_type = connection_type

    def set_addr(self, addr):
        """ip address:port or com port or ip addrres for visa"""
        self.dev_addr = addr

    def connect(self):
        for con_class in context.connections_classes.values():
            if con_class.connection_type == self.connection_type:
                self.connection = con_class(self.dev_addr)
                break
            
        if not self.connection:
            raise ConnectionClassNotFoundError(self.connection_type)
        
        self.connection.connect()
        self.status = 'idle'
        self.q.put(f'\n{self.dev_name} connected to {self.dev_addr}')

    def close(self):
        self.connection.close()
        self.status = 'init'
        self.q.put(f'\n{self.dev_name} disconnected from {self.dev_addr}')

    def send(self, data):        
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {data}')
        self.connection.send(data)

    def read(self):
        ans = self.connection.read()
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nrecieved: {ans}')

    def io(self, data):
        ans = self.connection.io(data)
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {data}\nrecieved: {ans}')
        return ans

    @abstractmethod
    def init(self):
        pass