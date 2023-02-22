from itertools import chain

from analyzes.abstract import AbstractAnalyze
from analyzes.decorators import plot_results
from core.utils import plot_traces

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

    @plot_results
    def run(self):
        for device in chain([self.emitter,], self.meters):
            device.set_wavelen(self.wavelen)

        for device in chain([self.emitter,], self.meters):
            device.set_power(self.power)

        self.emitter.set_beam_on()

        results = []
        for meter in self.meters:
            res = meter.get_power()
            results.append({'device': device.label, 'res': res, 'wavelen': self.wavelen})

            for ch, r in enumerate(res):
                trace_id = f'{meter.label}__{ch}'
                self.add_values_to_trace(trace_id, float(self.wavelen), float(r))

        self.emitter.set_beam_on()

    def stop(self):
        pass
