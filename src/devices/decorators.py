from functools import wraps

import eel

def process_status(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if getattr(self, 'block_status', False):
            return fn(self, *args, **kwargs)
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

def need_block(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        mode_idx = 0
        block_idx = 0
        block = False
        for i, arg in enumerate(args):
            if arg == 'mode':
                mode_idx = i
            if arg == 'block':
                block_idx = i
        
        if mode_idx + 1 == block_idx:
            block = True
        
        ret = fn(self, block, *args, **kwargs)
        return ret
    return wrapper