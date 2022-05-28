from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from core.context import Context
from core.exceptions import DeviceNotFoundError, ConnectionError
from core.logs.log import LoggingQueue
from itf_modules.utils import set_status_light

context = Context()
q = LoggingQueue()

# class Worker(QObject):
#     message = pyqtSignal(object, str)
#     running = False
    
#     @pyqtSlot()
#     def process(self, widget, dev_name):
#         dev_dict = context.get_device(dev_name)
#         if not dev_dict:
#             raise DeviceNotFoundError()
        
#         self.message.emit(widget, 'processing')
#         try:
#             dev_dict.get('instance').init()
#         except ConnectionError as e:
#             q.put(e)
#             self.message.emit(widget, 'error')
#             return
        
#         self.message.emit(widget, 'ready')
                
class PowerPanHandler():

    def setup_power_pan(self, MainWindow):
        self.init_power_pan_widgets()
        
        self.handle_power_signals()
        
    def init_power_pan_widgets(self):
        self.nest__powerLaserCombo()
        
    def nest__powerLaserCombo(self):
        for device in context.devices:
            if device['instance'].dev_type == 'laser' and device['instance'].status != 'init':
                self.powerLaserCombo.addItem(device['instance'].dev_name)
            
    def handle_power_signals(self):        
        self.startPowerMeasBtn.clicked.connect(self.handle_power_meas)
        
    def handle_power_meas(self):
        print('measuring')