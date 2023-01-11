from abc import ABCMeta, abstractmethod

from core.utils import get_device_by_label

class AbstractAnalyze(metaclass=ABCMeta):
    analyse_name = ''
    emitter = None  # laser or wideband oscilator
    meters = []  # list of selected meters
    wavelen = None  # value for single or contimues meas
    power = None
    traces = []

    @abstractmethod
    def set_wavelen(self, value):
        pass

    @abstractmethod
    def set_wavelen_range(self, wavelen_min, wavelen_max):
        pass

    @abstractmethod
    def set_power(self, value):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def clear_traces(self):
        self.traces = []

    def set_meters(self, devices_labels):
        for label in devices_labels:
            device = get_device_by_label(label)
            self.meters.append(device)

    def set_emitter(self, device_label):
        device = get_device_by_label(device_label)
        self.emitter = device
