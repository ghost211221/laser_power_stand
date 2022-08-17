

class Context():
    """ Class that contains all states of program"""

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Context, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.run_cont_measure = False
        self.run_single_measure = False
        self.run_scan = False
        self.run_laser = False
        self.exit_mode = False

        self.current_wavelen = None
        self.current_power = None

        self.single_meas_results = {}
        self.scan_meas_results = {}

    def get_device(self, device_name):
        for device in self.devices:
            if device['dev_name'] == device_name:
                return device