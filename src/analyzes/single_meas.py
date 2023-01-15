from itertools import chain

from src.analyzes.abstract import AbstractAnalyze

class SingleMeas(AbstractAnalyze):
    """
    Make measure by click with selected devices
    """

    analyse_name = 'single_meas'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingleMeas, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        super().__init__()

    def run(self):
        for device in chain(self.emitter, self.meters):
            device.set_wavelen(self.wavelen)

        for device in chain(self.emitter, self.meters):
            device.set_power(self.power)

        results = []
        for meter in self.meters:
            res = meter.get_power()
            results.append({'device': device.label, 'res': res, 'wavelen': self.wavelen})

    def stop(self):
        pass
