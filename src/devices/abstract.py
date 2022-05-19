from abc import ABCMeta, abstractmethod
from re import A

class AbstractDevice(metaclass=ABCMeta):
    connection = None
    connection_type = None
    connection_types = []
    dev_name = None
    dev_addr = None
    timeout = None

    @abstractmethod
    def set_connection(self, connection_type):
        pass

    @abstractmethod
    def set_addr(self, addr):
        """ip address:port or com port or ip adrres for visa"""
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def io(self, data):
        pass

    @abstractmethod
    def init(self):
        pass