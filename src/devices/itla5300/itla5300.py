import os
from copy import copy
import struct
import logging
import time

import yaml

from ..abstract import AbstractDevice
from src.core.context import Context
from src.core.exceptions import ConnectionError
from src.core.utils import mW_to_dBm

from src.devices.decorators import process_status, need_block

log = logging.getLogger(__name__)
c = Context()

class Helper():
    """build cmd and convert to bytes with control sum"""
    def __init__(self):
        self._cmd_int = 0

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

    def decode_response(self, response):
        _response = int.from_bytes(response, byteorder='big', signed=True)

        status = _response & 3<<24
        value = _response & 65535

        return status, value


class ITLA5300(AbstractDevice):

    connection_types = ['com']
    dev_name = 'ITLA5300'
    dev_type = 'laser'
    wavelen_min = 1527.6
    wavelen_max = 1568.6

    def __init__(self, label):
        super().__init__(label)
        self.baudrate = None
        self.__helper = Helper()

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate

    @process_status
    def init(self, *args, **kwargs):
        with open(os.path.join(os.path.dirname(__file__), 'init_proc.yml')) as f:
            data = yaml.safe_load(f)

        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        self.q.put(f'\nInit {self.dev_name} on {self.dev_addr}')
        for i, data_set in enumerate(data):
            if c.exit_mode:
                self.q.put(f'{self.dev_name} breaking init loop for exit...')
                break

            try:
                self.__helper.setRW(data_set['rw'])
                self.__helper.setRegData(data_set['data'])
                self.__helper.setRegAddr(data_set['cmd'])
            except KeyError as e:
                log.error(f'failed to get operation {i+1}')
                continue

            bytes_ = self.__helper.genData()

            try:
                ans = self.io(bytes_)
                # self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes_)}\nrecieved: {ans}')
                log.info(f'{i:4}: {self.dev_name} on {self.dev_addr}\nsent: {str(bytes_)}\nrecieved: {ans}')

            except Exception as e:
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                raise Exception(e)

        self.q.put(f'\nInit {self.dev_name} on {self.dev_addr} done')

    # @process_status
    def set_wavelen(self, wave_len, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        # calculate frequency in THz
        freq = 299792458 / float(wave_len) / 10 ** 3
        fcf1 = int(freq)
        freq_ = (freq - fcf1) * 10 ** 4
        fcf2 = int(freq_)
        freq_ -= fcf2
        fcf3 = int(freq_ * 10 ** 2)

        cmds = [
            (1, 53, fcf1),
            (1, 54, fcf2),
            (1, 103, fcf3),
        ]

        # put to regs
        self.q.put(f'\nSet frequency {freq}MHz on {self.dev_name} on ')

        for cmd in cmds:
            self.__helper.setRW(cmd[0])
            self.__helper.setRegData(cmd[2])
            self.__helper.setRegAddr(cmd[1])
            bytes_ = self.__helper.genData()
            try:
                ans = self.send(bytes_)
                self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
                log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes)}\nrecieved: {ans}')
            except Exception as e:
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')

    # @process_status
    def set_power(self, power, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        cmds = [
            (1, 49, mW_to_dBm(power) * 100),
        ]

        # put to regs
        self.q.put(f'\nSet power {power}mW on {self.dev_name} on ')

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

    @process_status
    @need_block
    def set_beam_on(self, block=False, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        cmds = [
            (1, 0x32, 8),
        ]

        # put to regs
        self.q.put(f'\nEnabling beam on {self.dev_name} on ')

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
        
        status, val = self.get_beam_state()
        if status != 0:
            return 'Failed to enable beam'
     
        while block and val != 8:
            status, val = self.get_beam_state()
            time.sleep(0.1)

        time.sleep(0.2)

        if status == 0 and val == 8:
            self.q.put(f'\nBeam enabled')

    @process_status
    def set_beam_off(self, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        cmds = [
            (1, 0x32, 0),
        ]

        # put to regs
        self.q.put(f'\nDisabling beam {self.dev_name}')

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

    @process_status
    def get_beam_state(self, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        cmd = (0, 0x32, 0)

        # put to regs
        self.q.put(f'\Getting beam status on {self.dev_name}')

        self.__helper.setRW(cmd[0])
        self.__helper.setRegData(cmd[2])
        self.__helper.setRegAddr(cmd[1])
        _bytes = self.__helper.genData()
        try:
            ans = self.io(_bytes)
            self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(_bytes)}\nrecieved: {ans}')
            log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(_bytes)}\nrecieved: {ans}')
            status, state =  self.__helper.decode_response(ans)

            return status, state == 8
        
        except Exception as e:
            log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
            self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')

            return -1, False            

    def can_set_wavelen(self, value):
        if value and isinstance(value, (int, float)):
            return self.wavelen_min <= value <= self.wavelen_max

        raise Exception(f'Can`t set wavelen="{value}"')

    def can_set_power(self, value):
        return True

    def get_temperature(self, *args, **kwargs):
        if not self.connection or not self.connection.connected:
            raise ConnectionError(f'Device {self.dev_name} is not connected')

        # cmd = (0, 67, 0)
        cmd = (0, 0x58, 0)

        # put to regs
        self.q.put(f'\nGetting temperature {self.dev_name}')

        self.__helper.setRW(cmd[0])
        self.__helper.setRegData(cmd[2])
        self.__helper.setRegAddr(cmd[1])
        bytes_ = self.__helper.genData()
        try:
            ans = self.io(bytes_)
            self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes_)}\nrecieved: {ans}')
            log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes_)}\nrecieved: {ans}')
        except Exception as e:
            log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
            self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
            return -1, 'failed to get temperatue'
        
        status, n = self.__helper.decode_response(ans)

        cmd = (0, 0x0B, 0)
        temps = []
        while n > 0:
            self.__helper.setRW(cmd[0])
            self.__helper.setRegData(cmd[2])
            self.__helper.setRegAddr(cmd[1])
            bytes_ = self.__helper.genData()
            try:
                ans = self.io(bytes_)
                self.q.put(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes_)}\nrecieved: {ans}')
                log.info(f'{self.dev_name} on {self.dev_addr}\nsent: {str(bytes_)}\nrecieved: {ans}')
            except Exception as e:
                log.exception(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                self.q.put(f'failed to communicate {self.dev_name} on {self.dev_addr}.\nError:\n{e}')
                return -1, 'failed to get temperatue'

            status, val = self.__helper.decode_response(ans)
            temps.append(val)
            n -= 2
            
        return round(max(temps) / 100, 2), ''



if __name__ == '__main__':
    helper = Helper()

    helper.setRW(0)
    helper.setRegAddr(37)
    helper.setRegData(271)

    print(helper.genData())
