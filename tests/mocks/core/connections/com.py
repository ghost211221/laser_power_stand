import yaml

def decode_data(data):
    pass

class Com():
    connection_type = 'com'
    
    def __init__(self, comport, timeout=1, baudrate=9600):
        print('called mocked constructor')
        self.__comport = comport
        self.__port = None
        self.__timeout = timeout
        self.__baudrate = baudrate

    def connect(self):
        self.connected = True

    def close(self):
        self.connected = False

    def send(self, data):
        pass

    def read(self, data):
        pass

    def io(self, data):
        with open('../../../../src/devices/itla5300/init_proc.yml') as f:
            cmds = yaml.safe_load_all(f)
            
        
        