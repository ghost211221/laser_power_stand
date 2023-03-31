from functools import wraps

from core.utils import plot_traces

def plot_results(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        ret = fn(self, *args, **kwargs)
        if self.should_plot:
            plot_traces(self.analyse_name, self.traces)

        return ret
    return wrapper