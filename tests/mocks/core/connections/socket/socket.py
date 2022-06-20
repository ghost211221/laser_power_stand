import yaml

from src.core.exceptions import ConnectionError
from src.core.connections.abstract import AbstractConnection

from tests.mocks.uut import UUT


uut = UUT()


def decode_data(data):
    pass

class Socket():
    connection_type = 'socket'
    
    def __init__(self, addr, timeout=1):
        print('called mocked constructor')
        self.__addr = addr
        self.__ip = None
        self.__port = None
        self.__timeout = timeout

    def connect(self):
        self.__ip, self.__port = self.__addr.split(':')
        if not (self.__ip and self.__port):
            self.connected = False
            raise ConnectionError(f'ip or port not found in {self.__addr}')
        
        self.connected = True

    def close(self):
        self.connected = False

    def send(self, data):
        pass

    def read(self):
        pass

    def io(self, cmd):  
        if 'IDN?' in cmd:
            return 'FIBERPRO,MCOPM,0,Ver. X.y\r\n'
        
        if 'READ? 0' in cmd:
            return ','.join([str(uut.power), str(uut.power), str(uut.power), str(uut.power)]).encode()
            
        
        