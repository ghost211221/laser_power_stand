from abc import ABCMeta, abstractmethod

from core.context import Context


c = Context()

class AbstractAnalyze(metaclass=ABCMeta):
    emitter = None  # laser or wideband oscilator
    meters = []  # list of selected meters
    wavelen = None  # value for single or contimues meas
    power = None
    traces = []

    @abstractmethod
    def set_wavelen(self, value):
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
        self.meters = []
        for device in c.devices:
            if device.label in devices_labels:
                self.meters.append(device)


    def set_emitter(self, device_label):
        for device in c.devices:
            if device.label == device_label:
                self.emitter = device
