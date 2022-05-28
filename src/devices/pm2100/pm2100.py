import logging


from ..abstract import AbstractDevice
from core.context import Context
from core.exceptions import ConnectionError


log = logging.getLogger(__name__)


class PM2100(AbstractDevice):

    connection_types = ['socket']
    dev_name = 'PM2100'
    dev_type = 'power_meter'

    def __init__(self):
        super().__init__()
        self.baudrate = None

    def set_timeout(self, timeout):
        self.timeout = timeout
        
    def init(self):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')            
            
        self.q.put(f'\nInit {self.dev_name} on {self.dev_addr}')
        self.status = 'processing'
        
        cmd = '*IDN?'
        ans = self.io(f'{cmd}\r\n')
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {cmd}\nrecieved: {ans}')
        log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')                
                
        self.send('AVG 0.5\r\n')
        self.status = 'ready'
    
    def set_wavelen(self, wavelen):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')            
            
        self.q.put(f'\nInit {self.dev_name} on {self.dev_addr}')
        self.status = 'processing'
        
        cmd = f'WAV {wavelen}'
        ans = self.send(f'{cmd}\r\n')
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {cmd}\nrecieved: {ans}')
        log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')                

        self.status = 'ready'
    
    def get_power(self):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')            
            
        self.q.put(f'\nInit {self.dev_name} on {self.dev_addr}')
        self.status = 'processing'
        
        cmd = 'READ? 0'
        ans = self.io(f'{cmd}\r\n')
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {cmd}\nrecieved: {ans}')
        log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')                

        self.status = 'ready'
        
        return ans.decode().strip().split(',')
        