from time import sleep
from threading import Thread

from itertools import chain

from .abstract import AbstractAnalyze

from core.queues import TasksQueue


tq = TasksQueue()

def get_device_ch(dev_ch_str):
    return dev_ch_str.split('__')

class ContMeas(AbstractAnalyze):
    """
    Make measure by click with selected devices
    """

    analyse_name = 'cont_meas'
    can_run = False
    selected_meters_channels = []
    measure_thread = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ContMeas, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()

    def make_analyse(self):
        self.can_run = True
        for device in chain([self.emitter,], self.meters):
            device.block_status = True
            device.set_status('processing')

        for device in chain([self.emitter,], self.meters):
            device.set_wavelen(self.wavelen)
            device.set_power(self.power)

        # enable laser
        tq.put(([self.emitter.label, ], 'set_beam_on', ['mode', 'block']))

        while self.can_run:
            sleep(1)

            # make measure
            meters_labs = [m.label for m in self.meters]
            tq.put((meters_labs, 'get_power', ['callback', 'push_cont_data']))

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
