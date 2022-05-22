from threading import Thread

from core.context import Context
from core.exceptions import DeviceNotFoundError

context = Context()

class DevicesPanHandler():

    def setup_devices_pan(self, MainWindow):
        self.init_widgets()
        
        self.handle_signals()
        
    def init_widgets(self):
        for port in context.comports:
            self.laserITLAComPortCombo.addItem(port)
            
        if context.comports:
            self.itlaConnection.setEnabled(True)
            
        else:
            self.itlaConnection.setEnabled(False)
            
    def handle_signals(self):
        self.laserITLAComPortCombo.currentIndexChanged.connect(self.handle_itla_comport_select)
        self.itlaConnection.clicked.connect(self.handle_itla_connect)
        
    def handle_itla_comport_select(self):
        self.itlaConnection.setEnabled(True)
        
    def handle_itla_connect(self):
        dev_dict = context.get_device('ITLA5300')
        if not dev_dict:
            raise DeviceNotFoundError('ITLA5300')
        
        dev_dict.get('instance').set_connection(self.laserITLAComTypeCombo.currentText())
        dev_dict.get('instance').set_addr(self.laserITLAComPortCombo.currentText())
        
        dev_dict.get('instance').connect()
        # all device operations are in threads!
        itla5300_init_thread = Thread(target=dev_dict.get('instance').init)
        itla5300_init_thread.start()
        
