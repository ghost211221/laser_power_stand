from abc import ABCMeta, abstractmethod

from src.analyzes.decorators import plot_results

class Replace():
    pass


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
    emitter_ready = False
    should_plot = True

    def __init__(self):
        self.traces = []

    def set_wavelen(self, value):
        self.wavelen = value

    def set_wavelen_min(self, value):
        self.wavelen_start = float(value)

    def set_wavelen_max(self, value):
        self.wavelen_stop = float(value)

    def set_wavelen_step(self, value):
        self.wavelen_step = float(value)

    def set_power(self, value):
        self.power = float(value)

    def add_device_traces(self, device):
        if device.dev_type != 'power_meter':
            return

        for ch in range(device.chanels):
            self.traces.append({
                'id': f'{device.label}__{ch}',
                'title': f'{device.label} {ch+1}',
                'data': {

                }
            })

    def delete_traces(self, device):
        if device.dev_type != 'power_meter':
            return

        for ch in range(device.chanels):
            trace_id = f'{device.label}__{ch}'
            for i, trace in enumerate(self.traces):
                try:
                    if trace.get('id') == trace_id:
                        self.traces[i] = Replace()
                except Exception:
                    pass
                
        self.traces = list(filter(lambda t: not isinstance(t, Replace), self.traces))

    @plot_results
    def plot(self):
        pass
    
    def add_values_to_trace(self, trace_id, x, y):
        for trace in self.traces:
            if trace.get('id') == trace_id:
                trace['data'][x] = y
                return

        raise Exception(f'trace {trace_id} not found!')

    def mark_emitter_ready(self):
        self.emitter_ready = True

    def mark_emitter_off(self):
        self.emitter_ready = False

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
        for trace in self.traces:
            trace['data'] = {}

    def set_meters(self, devices):
        self.meters = devices

    def set_emitter(self, device):
        self.emitter = device
