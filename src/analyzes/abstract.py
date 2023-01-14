from abc import ABCMeta, abstractmethod

from core.utils import get_device_by_label

class AbstractAnalyze(metaclass=ABCMeta):
    analyse_name = ''
    emitter = None  # laser or wideband oscilator
    meters = []  # list of selected meters
    wavelen = 1527.6  # value for single or contimues meas
    power = 7.58
    wavelen_start = 1527.6
    wavelen_stop = 1568.6
    wavelen_step = 0.005
    traces = []

    def set_wavelen(self, value):
        self.wavelen = value

    def set_wavelen_min(self, value):
        self.wavelen_start = value

    def set_wavelen_max(self, value):
        self.wavelen_stop = value

    def set_wavelen_step(self, value):
        self.wavelen_step = value

    def set_power(self, value):
        self.power = value

    @property
    def can_run(self):
        return self.emitter and self.meters

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def clear_traces(self):
        self.traces = []

    def set_meters(self, devices):
        self.meters = devices

    def set_emitter(self, device):
        self.emitter = device
