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
        
        with open('src/devices/itla5300/init_proc.yml') as f:
            self.__cmds = yaml.safe_load(f)

    def connect(self):
        self.connected = True

    def close(self):
        self.connected = False

    def send(self, data):
        pass

    def read(self, data):
        pass
    
    def __extract_int(self, line):
        value = 0
        for i, digit in enumerate(list(reversed(line))):
            try:
                value += int(digit) * 16 ** i
            except ValueError:
                value += (ord(digit) - 65 + 10) * 16 ** i

        return value

    
    def __decode_cmd(self, bytes_arr):
        rw = None
        cmd = None
        data = None
        for i, byte in enumerate(bytes_arr):
            if i == 0:
                # proress r/w bit
                rw = byte & 0x1

            elif i == 1:
                # process cmd
                cmd = byte

            elif i == 2:
                data = byte << 8

            else:
                data += byte
                
        return rw, cmd, data

    def io(self, cmd):  
        rw, cmd_, data = self.__decode_cmd(cmd)
        for cmd_dict in  self.__cmds:
            if cmd_dict.get('rw') == rw and cmd_dict.get('cmd') == cmd_ and cmd_dict.get('data') == data:
                return cmd_dict.get('ans').encode()
        
            
        
        