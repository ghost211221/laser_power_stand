from time import sleep
from threading import Thread

from itertools import chain

from .abstract import AbstractAnalyze
from core.utils import plot_traces

from core.queues import TasksQueue


tq = TasksQueue()


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

        # clear previous traces and create new
        for device in self.meters:
            self.delete_traces(device)
            self.add_device_traces(device)

        for device in chain([self.emitter,], self.meters):
            device.block_status = True
            device.set_status('processing')

        self.wavelen = self.wavelen_start
        enabled = False

        count = 10

        meters_labs = [m.label for m in self.meters]
        while self.can_run and self.wavelen <= self.wavelen_stop:

            for device in chain([self.emitter,], self.meters):
                tq.put((device.label, 'set_wavelen', ['value', self.wavelen]))
                tq.put((device.label, 'set_power', ['value', self.power]))

            # enable laser
            if not enabled:
                tq.put(([self.emitter.label, ], 'set_beam_on', ['mode', 'block']))
                enabled = True

            # make measure
            tq.put((meters_labs, 'get_power', ['callback', 'add_measres_to_traces', 'analyse', 'scan_meas']))

            # if count > 0:
            #     count -= 1
            # else:
            #     tq.put(([self.emitter.label, ], 'get_temperature', ['callback', 'show_temp']))
            #     count = 10
            
            self.wavelen += self.wavelen_step

        # disable laser
        tq.put(([self.emitter.label, ], 'set_beam_off', []))

        for device in chain([self.emitter,], self.meters):
            device.block_status = True
            device.set_status('ready')

    def run(self):
        self.measure_thread = Thread(target=self.make_analyse)
        self.measure_thread.start()

    def stop(self):
        self.can_run = False
        tq.clear()
        # disable laser
        tq.put(([self.emitter.label, ], 'set_beam_off', []))
