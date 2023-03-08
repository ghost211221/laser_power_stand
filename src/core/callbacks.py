import eel

from src.core.context import Context


c = Context()

def mark_emitter_ready(*args):
    pass

def add_measres_to_traces(res, device, *args):
    analyse_name = None
    for arg in args:
        if isinstance(arg, (list, tuple)):
            if arg[0] == 'analyse':
                analyse_name = arg[1]
                break

    if analyse_name == None:
        raise Exception(f'No analyse found during measres to traces')
             
    analyse = c.get_analyse_by_name(analyse_name=analyse_name)
    for ch, r in enumerate(res):
        trace_id = f'{device.label}__{ch}'
        analyse.add_values_to_trace(trace_id, float(device.wavelen), float(r))

    analyse.plot()

def show_temp(val, *args):
    eel.show_temp(val[0], val[1])

def push_cont_data(res, device, *args):
    data = []
    for i in range(device.chanels):
        data.append({
            'id': f'{device.label}__{i}',
            'val': res[i]
        })

    res = eel.show_cont_data('cont_meas', data)()
    return res