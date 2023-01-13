from functools import wraps

import eel

def process_status(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        self.set_status('processing')
        eel.set_device_status(self.label, self.status)
        try:
            ret = fn(self, *args, **kwargs)

            if self.connection:
                self.set_status('ready')
            else:
                self.set_status('init')

            eel.set_device_status(self.label, self.status)
            return ret
        except Exception as e:
            self.set_status('error')
            eel.set_device_status(self.label, self.status)

    return wrapper