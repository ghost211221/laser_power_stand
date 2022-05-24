import yaml

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
            
        
        