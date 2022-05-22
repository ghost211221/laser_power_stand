

class Context():
    """ Class that contains all states of program"""

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Context, cls).__new__(cls)
        return cls.instance
    
    def get_device(self, device_name):
        for device in self.devices:
            if device['dev_name'] == device_name:
                return device