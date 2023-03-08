import logging


from ..abstract import AbstractDevice
from src.core.context import Context
from src.core.exceptions import ConnectionError

from src.devices.decorators import process_status

log = logging.getLogger(__name__)


class PM2100(AbstractDevice):

    connection_types = ['socket']
    dev_name = 'PM2100'
    dev_type = 'power_meter'
    chanels = 4

    def __init__(self, label):
        super().__init__(label)
        self.baudrate = None

    def set_timeout(self, timeout):
        self.timeout = timeout

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

        cmd = 'READ? 0'
        ans = self.io(f'{cmd}\r\n')
        self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {cmd}\nrecieved: {ans}')
        log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')

        return ans.decode().strip().split(',')

    def set_wavelen(self, wave_len, *args, **kwargs):
        self.wavelen = wave_len