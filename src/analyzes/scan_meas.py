from time import sleep
from threading import Thread

from itertools import chain

from src.analyzes.abstract import AbstractAnalyze
from src.core.utils import plot_traces


def get_device_ch(dev_ch_str):
    return dev_ch_str.split('__')

class ScanMeas(AbstractAnalyze):
    """
    Make measure by click with selected devices
    """

    analyse_name = 'scan_meas'
    can_run = False
    selected_meters_channels = []
    measure_thread = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ScanMeas, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()

    def make_analyse(self):
        self.can_run = True
        for device in chain([self.emitter,], self.meters):
            device.block_status = True
            device.set_status('processing')

        self.wavelen = self.wavelen_start
        while self.can_run and self.wavelen <= self.wavelen_stop:
            for device in chain([self.emitter,], self.meters):
                device.set_wavelen(self.wavelen)
                device.set_power(self.power)

            results = []
            for meter in self.meters:
                res = meter.get_power()
                results.append({'device': device.label, 'res': res, 'wavelen': self.wavelen})

                for ch, r in enumerate(res):
                    trace_id = f'{meter.label}__{ch}'
                    self.add_values_to_trace(trace_id, float(self.wavelen), float(r))

            plot_traces(self.analyse_name, self.traces)

            sleep(1)
            self.wavelen += self.wavelen_step

        for device in chain([self.emitter,], self.meters):
            device.block_status = True
            device.set_status('ready')

    def run(self):
        self.measure_thread = Thread(target=self.make_analyse)
        self.measure_thread.start()

    def stop(self):
        self.can_run = False
