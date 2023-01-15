from abc import ABCMeta, abstractmethod
import logging

from core.context import Context
from core.exceptions import ConnectionClassNotFoundError, ConnectionError
from core.logs.log import LoggingQueue

from devices.decorators import process_status

log = logging.getLogger(__name__)
context = Context()

class AbstractDevice(metaclass=ABCMeta):
    connection = None
    connection_type = None
    connection_types = []
    label = None
    dev_name = None
    dev_addr = None
    dev_type = None
    timeout = None
    status = 'init'
    chanels = 1

    valid_statuses = ['init', 'processing', 'ready', 'error']

    def __init__(self, label):
        self.q = LoggingQueue()
        self.label = label

    def set_connection(self, connection_type):
        self.connection_type = connection_type

    def set_addr(self, addr):
        """ip address:port or com port or ip addrres for visa"""
        self.dev_addr = addr

    def set_status(self, status):
        if status in self.valid_statuses:
            self.status = status
            return

        raise Exception(f'Unknown status {status}')

    @process_status
    def connect(self, *args, **kwargs):
        for con_class in context.connections_classes.values():
            if con_class.connection_type == self.connection_type.lower():
                self.connection = con_class(self.dev_addr)
                break

        if not self.connection:
            raise ConnectionClassNotFoundError(self.connection_type)

        try:
            self.connection.connect()
        except Exception as e:
            self.q.put(f'\n{self.dev_name} failed to connect to {self.dev_addr}')
            raise ConnectionError('Не удалось подключиться к прибору {self.label}: {e}')

        self.q.put(f'\n{self.dev_name} connected to {self.dev_addr}')

    @process_status
    def close(self, *args, **kwargs):
        self.connection.close()
        self.connection = None
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

    @process_status
    @abstractmethod
    def init(self):
        pass

    @process_status
    def set_power(self, value):
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
