from time import sleep

from itertools import chain

from src.analyzes.abstract import AbstractAnalyze
from src.core.utils import push_cont_data


def get_device_ch(dev_ch_str):
    return dev_ch_str.split('__')

class ContMeas(AbstractAnalyze):
    """
    Make measure by click with selected devices
    """

    analyse_name = 'cont_meas'
    can_run = False
    selected_meters_channels = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ContMeas, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()

    def run(self):
        self.can_run = True
        while self.can_run:
            sleep(1)
            res_dict = []
            for device in chain([self.emitter,], self.meters):
                device.set_wavelen(self.wavelen)

            for device in chain([self.emitter,], self.meters):
                device.set_power(self.power)

            results = []
            for meter in self.meters:
                res = meter.get_power()
                results.append({'device': device.label, 'res': res, 'wavelen': self.wavelen})

                for ch, r in enumerate(res):
                    res_id = f'{meter.label}__{ch}'
                    res_dict.append({
                        'id': res_id,
                        'val': r
                    })

            push_cont_data(self.analyse_name, res_dict)

    def stop(self):
        self.can_run = False
