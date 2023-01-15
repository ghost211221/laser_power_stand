from abc import ABCMeta, abstractmethod


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
        self.set_power.set_wavelen(self.power)

    def gen_traces(self):
        self.traces = []
        for meter in self.meters:
            for ch in meter.chanels:
                self.traces.append({
                    'id': f'{meter.label}__{ch}',
                    'title': f'{meter.label} {ch+1}',
                    'x': [],
                    'y': []
                })

        

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
