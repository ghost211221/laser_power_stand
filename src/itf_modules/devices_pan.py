from core.context import Context

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
        context.devices.get('ITLA5300').get('instance').set_connection(self.laserITLAComTypeCombo.currentText())
        context.devices.get('ITLA5300').get('instance').set_addr(self.laserITLAComPortCombo.currentText())
        
        context.devices.get('ITLA5300').get('instance').connect()
