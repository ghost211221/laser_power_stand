import eel

from core.context import Context


c = Context()

@eel.expose
def set_emitter(analysis_name, device_label):
    if not analysis_name or not device_label:
        return {'status': 'fail', 'message': 'no device or analysis'}

    analysis = c.get_analyse_by_name(analysis_name)
    device = c.get_device_by_lab(device_label)
    if not analysis:
        raise Exception(f'No analysis found: "{analysis_name}"')
    if not device:
        raise Exception(f'No device found: "{device_label}"')

    analysis.set_emitter(device)

    return {'status': 'success', 'message': ''}

@eel.expose
def set_meters(analysis_name, devices_recs):
    devices_labels = set([i['device'] for i in devices_recs])
    if not analysis_name or not devices_labels:
        return {'status': 'fail', 'message': 'no devices or analysis'}

    analysis = c.get_analyse_by_name(analysis_name)
    if not analysis:
        raise Exception(f'No analysis found: "{analysis_name}"')
    devices = []
    for device_label in devices_labels:
        device = c.get_device_by_lab(device_label)
        if not device:
            raise Exception(f'No device found: "{device_label}"')

        devices.append(device)

    analysis.set_meters(devices)

    return {'status': 'success', 'message': ''}

@eel.expose
def set_wavelen(analysis_name, wavelen):
    if not analysis_name or not wavelen:
        return {'status': 'fail', 'message': 'no wavelen or analysis'}

    analysis = c.get_analyse_by_name(analysis_name)
    if not analysis:
        raise Exception(f'No analysis found: "{analysis_name}"')

    analysis.set_wavelen(wavelen)

    return {'status': 'success', 'message': ''}

@eel.expose
def set_wavelen_range(analysis_name, wavelen_min, wavelen_max, step):
    if not analysis_name or not wavelen_min or not wavelen_max:
        return {'status': 'fail', 'message': 'no wavelenghts or analysis'}

    analysis = c.get_analyse_by_name(analysis_name)
    if not analysis:
        raise Exception(f'No analysis found: "{analysis_name}"')

    analysis.set_wavelen_min(wavelen_min)
    analysis.set_wavelen_max(wavelen_max)
    analysis.set_wavelen_step(step)

    return {'status': 'success', 'message': ''}

@eel.expose
def set_power(analysis_name, power):
    if not analysis_name or not power:
        return {'status': 'fail', 'message': 'no power or analysis'}

    analysis = c.get_analyse_by_name(analysis_name)
    if not analysis:
        raise Exception(f'No analysis found: "{analysis_name}"')

    analysis.set_power(power)

    return {'status': 'success', 'message': ''}

@eel.expose
def clear_traces(analysis_name):
    if not analysis_name:
        return {'status': 'fail', 'message': 'no analysis'}

    analysis = c.get_analyse_by_name(analysis_name)
    if not analysis:
        raise Exception(f'No analysis found: "{analysis_name}"')

    analysis.clear_traces()

    return {'status': 'success', 'message': ''}

@eel.expose
def run_analysis(analysis_name):
    if not analysis_name:
        return {'status': 'fail', 'message': 'no analysis'}

    analysis = c.get_analyse_by_name(analysis_name)
    if not analysis:
        raise Exception(f'No analysis found: "{analysis_name}"')

    analysis.run()

    return {'status': 'success', 'message': ''}


@eel.expose
def stop_analysis(analysis_name):
    if not analysis_name:
        return {'status': 'fail', 'message': 'no analysis'}

    analysis = c.get_analyse_by_name(analysis_name)
    if not analysis:
        raise Exception(f'No analysis found: "{analysis_name}"')

    analysis.stop()

    return {'status': 'success', 'message': ''}
