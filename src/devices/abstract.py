from abc import ABCMeta, abstractmethod
import logging

from core.context import Context
from core.exceptions import ConnectionClassNotFoundError, ConnectionError
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
    chanels = 1
    
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
        
        try:
            self.connection.connect()
        except Exception:
            self.status = 'error'
            self.q.put(f'\n{self.dev_name} failed to connect to {self.dev_addr}')
            return
            
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
    
    @property
    def labels(self):
        """labels for showing line names in plots"""
        if self.chanels > 1:
            return [f'{self.dev_name} {i}' for i in range(self.chanels)]
        
        return [self.dev_name, ] 
    
    @property
    def keys(self):
        if self.chanels > 1:
            return [f'{self.dev_name.lower()}_{i}' for i in range(self.chanels)]
        
        return [self.dev_name.lower(), ] 