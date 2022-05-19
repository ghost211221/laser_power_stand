from copy import copy
import struct
import logging

import yaml

from ..abstract import AbstractDevice
from core.context import Context
from core.logs.log import LoggingQueue
from core.exceptions import ConnectionError

# mock connection module for if have no access to devices
if Context().run_mode == 'testing':
    from tests.mocks.core.connections.com import Com
elif Context().run_mode == 'normal':
    from core.connections.com.com import Com
else:
    raise Exception(f'Unkonwn mode "{Context().run_mode}"')


log = logging.getLogger(__name__)


class Helper():
    """build cmd and convert to bytes with control sum"""
    def __init__(self):
        self._cmd_int = 0
        self._response = b''
        self._bytes_line = b''
        self._int_arr = []

    def _gen_int_arr(self):
        self._int_arr = []
        numOfDigits = 4
        data = copy(self._cmd_int)
        while numOfDigits > 0:
            self._int_arr.append(data % 256)
            data = int(data / 256)
            numOfDigits -= 1

        self._int_arr.reverse()

    def _convertData(self):
        self._bytes_line = struct.pack('!{0}B'.format(len(self._int_arr)), *self._int_arr)

    def genData(self):
        self._convertData()
        return self._bytes_line

    def setCmdInt(self, val):
        if val < 0 or val > 4294967295:
            return 'Число должно быть в диапазлне от 0 до 4294967295'

        self._cmd_int = val

    def setRegAddr(self, reg_addr):
        if reg_addr < 0 or reg_addr > 255:
            return 'Номер регистра должен быть в диапазоне 0 - 255'

        self._cmd_int &= 16842751
        self._cmd_int |= reg_addr<<16

        self._calcCheckSum()

    def setRegData(self, data):
        if data < 0 or data > 65535:
            return 'Номер регистра должен быть в диапазоне 0 - 65535'

        self._cmd_int &= 33488896
        self._cmd_int |= data

        self._calcCheckSum()

    def setRW(self, rw):
        if rw not in (0, 1):
            return 'Значение должно быть 0 или 1'

        self._cmd_int &= 16777215
        self._cmd_int |= rw<<24

        self._calcCheckSum()

    def getCmdInt(self):
        return self._cmd_int

    def getCmdData(self):
        return self._cmd_int & 0xFF

    def getCmdReg(self):
        return self._cmd_int & 0xF00

    def getCmdRw(self):
        return self._cmd_int & 0x1000

    def _calcCheckSum(self):
        self._cmd_int &= 134217727

        self._gen_int_arr()

        bip8 = (self._int_arr[0] & 0x0f) ^ self._int_arr[1] ^ self._int_arr[2] ^ self._int_arr[3]
        bip4 = ((bip8 & 0xf0)>>4) ^ (bip8 & 0x0f)

        self._cmd_int |= bip4<<27
        self._gen_int_arr()


class ITLA5300(AbstractDevice):

    connection_types = ['com']
    dev_name = 'ITLA5300'

    def __init__(self):
        self.baudrate = None
        self.__helper = Helper()

    def set_connection(self, connection_type):
        self.connection_type = connection_type

    def set_addr(self, addr):
        self.dev_addr = addr

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate

    def connect(self):
        self.connection = Com(self.dev_addr)
        self.connection.connect()

    def send(self, data):
        self.connection.send(data)

    def read(self):
        self.connection.read()

    def io(self):
        self.connection.io()
        
    def init(self):
        with open('init_proc.yaml') as f:
            data = yaml.safe_load(f)
            
        if not self.connection or not self.connect.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')
            
            
        LoggingQueue().put(f'Init {self.dev_name} on {self.dev_addr}\n=============================')
        for data_set in data:
            self.__helper.setRW(data_set['rw'])
            self.__helper.setRegData(data_set['data'])
            self.__helper.setRegAddr(data_set['cmd'])
            
            bytes = self.__helper.genData()

            try:
                ans = self.connection.io(bytes)
                LoggingQueue().put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
                
            except Exception as e:
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
    