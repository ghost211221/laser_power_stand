from abc import ABCMeta, abstractmethod

class AbstractDevice(metaclass=ABCMeta):
    connection = None
    connetion_types = []
    dev_name = None

    @abstractmethod
    def set_connection(self, connection_type):
        pass