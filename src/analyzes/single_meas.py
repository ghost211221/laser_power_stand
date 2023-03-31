from itertools import chain

from .abstract import AbstractAnalyze

from core.queues import TasksQueue


tq = TasksQueue()

class SingleMeas(AbstractAnalyze):
    """
    Make measure by click with selected devices
    """

    analyse_name = 'single_meas'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingleMeas, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()
        self.emitter_ready = False
        self.should_plot = True

    def run(self):
        for device in chain([self.emitter,], self.meters):
            device.set_wavelen(self.wavelen)

        for device in chain([self.emitter,], self.meters):
            device.set_power(self.power)

        # enable laser
        tq.put(([self.emitter.label, ], 'set_beam_on', ['mode', 'block']))

        # make measure
        meters_labs = [m.label for m in self.meters]
        tq.put((meters_labs, 'get_power', ['callback', 'add_measres_to_traces', 'analyse', 'single_meas']))
        # disable laser
        tq.put(([self.emitter.label, ], 'set_beam_off', []))
        # plot will be called by callback

    def stop(self):
        pass
