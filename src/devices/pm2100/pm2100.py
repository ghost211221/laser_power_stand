import logging


from ..abstract import AbstractDevice
from core.context import Context
from core.exceptions import ConnectionError, DeviceSetUpError

from devices.decorators import process_status

log = logging.getLogger(__name__)


class PM2100(AbstractDevice):

    connection_types = ['socket']
    dev_name = 'PM2100'
    dev_type = 'power_meter'
    default_addr = '192.168.1.161:5000'
    modules = 5
    chanels = 4

    def __init__(self, label):
        super().__init__(label)
        self.baudrate = None

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_modules(self, modules):
        if modules < 1 or modules > 5:
            raise DeviceSetUpError(f'Can`t set up number of modules: {modules}')
        self.modules = modules

    @process_status
    def init(self, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        self.q.put(f'\nInit {self.dev_name} on {self.dev_addr}')
        cmd = '*IDN?'
        ans = self.io(f'{cmd}\r\n')
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {cmd}\nrecieved: {ans}')
        log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')

        self.send('AVG 0.5\r\n')

    @process_status
    def set_wavelen(self, wavelen, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        self.q.put(f'\nSet wavelen {wavelen}MHz on {self.dev_name} on ')

        cmd = f'WAV {wavelen}'
        ans = self.send(f'{cmd}\r\n')
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {cmd}\n')
        log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\n')

    @process_status
    def get_power(self, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        self.q.put(f'\nInit {self.dev_name} on {self.dev_addr}')

        ret = []
        for i in range(self.modules):
            cmd = f'READ? {i}'
            ans = self.io(f'{cmd}\r\n')
            self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {cmd}\nrecieved: {ans}')
            log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')

            ret.append(ans.decode().strip().split(','))
        
        return ret

    def set_wavelen(self, wave_len, *args, **kwargs):
        self.wavelen = wave_len