import os
from copy import copy
import struct
import logging

import yaml

from ..abstract import AbstractDevice
from core.context import Context
from core.exceptions import ConnectionError
from core.utils import mW_to_dBm

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
        self._cmd_int |= int(data)

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

        self._cmd_int |= bip4<<28
        self._gen_int_arr()


class ITLA5300(AbstractDevice):

    connection_types = ['com']
    dev_name = 'ITLA5300'
    dev_type = 'laser'

    def __init__(self):
        super().__init__()
        self.baudrate = None
        self.__helper = Helper()

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate

    def init(self):
        with open(os.path.join(os.path.dirname(__file__), 'init_proc.yml')) as f:
            data = yaml.safe_load(f)

        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        # every dict in data is doubled o_O
        # temporary way to fix
        should_pass_even = data[-2] == data[-1]

        print(len(data))
        self.q.put(f'\nInit {self.dev_name} on {self.dev_addr}')
        self.status = 'processing'
        for i, data_set in enumerate(data):
            if should_pass_even and i % 2 == 0:
                continue

            try:
                self.__helper.setRW(data_set['rw'])
                self.__helper.setRegData(data_set['data'])
                self.__helper.setRegAddr(data_set['cmd'])
            except KeyError as e:
                log.error(f'failed to get operation {i+1}')
                continue

            bytes_ = self.__helper.genData()

            try:
                print('----------')
                print(i)
                # print(bytes_)
                ans = self.io(bytes_)
                # print(ans)
                # self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes_)}\nrecieved: {ans}')
                log.info(f'{i:4}: {self.dev_name} on {self.dev_addr}\nsent: {str(bytes_)}\nrecieved: {ans}')

            except Exception as e:
                self.status = 'error'
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                break

        self.status = 'ready'

    def set_wavelen(self, wave_len):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        # calculate frequency
        freq = round(3 / wave_len * 10 ** 11)
        freq3 = freq % 100
        freq_ = freq // 100
        freq2 = freq_ % 10000
        freq1 = freq_ // 10000

        cmds = [
            (1, 53, freq1),
            (1, 54, freq2),
            (1, 103, freq3),
        ]

        # put to regs
        self.q.put(f'\nSet frequency {freq}MHz on {self.dev_name} on ')
        self.status = 'processing'

        for cmd in cmds:
            self.__helper.setRW(cmd[0])
            self.__helper.setRegData(cmd[2])
            self.__helper.setRegAddr(cmd[1])
            bytes = self.__helper.genData()
            try:
                ans = self.send(bytes)
                self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
                log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
            except Exception as e:
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')

        self.status = 'ready'

    def set_power(self, power):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        cmds = [
            (1, 49, mW_to_dBm(power) * 100),
        ]

        # put to regs
        self.q.put(f'\nSet power {power}mW on {self.dev_name} on ')
        self.status = 'processing'

        for cmd in cmds:
            self.__helper.setRW(cmd[0])
            self.__helper.setRegData(cmd[2])
            self.__helper.setRegAddr(cmd[1])
            bytes = self.__helper.genData()
            try:
                ans = self.send(bytes)
                self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
                log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
            except Exception as e:
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')

        self.status = 'ready'

    def set_beam_on(self):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        cmds = [
            (1, 50, 8),
        ]

        # put to regs
        self.q.put(f'\nEnabling beam on {self.dev_name} on ')
        self.status = 'processing'

        for cmd in cmds:
            self.__helper.setRW(cmd[0])
            self.__helper.setRegData(cmd[2])
            self.__helper.setRegAddr(cmd[1])
            bytes = self.__helper.genData()
            try:
                ans = self.send(bytes)
                self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
                log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
            except Exception as e:
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')


    def set_beam_off(self):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        cmds = [
            (1, 50, 0),
        ]

        # put to regs
        self.q.put(f'\nDisabling beam {self.dev_name} on ')
        self.status = 'processing'

        for cmd in cmds:
            self.__helper.setRW(cmd[0])
            self.__helper.setRegData(cmd[2])
            self.__helper.setRegAddr(cmd[1])
            bytes = self.__helper.genData()
            try:
                ans = self.send(bytes)
                self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
                log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
            except Exception as e:
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')

        self.status = 'ready'


if __name__ == '__main__':
    helper = Helper()

    helper.setRW(0)
    helper.setRegAddr(37)
    helper.setRegData(271)

    print(helper.genData())
