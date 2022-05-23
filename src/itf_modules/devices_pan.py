from threading import Thread

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from core.context import Context
from core.exceptions import DeviceNotFoundError, ConnectionError
from core.logs.log import LoggingQueue
from itf_modules.utils import set_status_light

context = Context()
q = LoggingQueue()

class Worker(QObject):
    message = pyqtSignal(object, str)
    running = False
    
    @pyqtSlot()
    def process(self, widget, dev_name):
        dev_dict = context.get_device(dev_name)
        if not dev_dict:
            raise DeviceNotFoundError()
        
        self.message.emit(widget, 'processing')
        try:
            dev_dict.get('instance').init()
        except ConnectionError as e:
            q.put(e)
            self.message.emit(widget, 'error')
            return
        
        self.message.emit(widget, 'ready')
                
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
            raise DeviceNotFoundError()
        
        if dev_dict.get('instance').status == 'init':
            port = self.laserITLAComPortCombo.currentText()
            if not port:
                return
            
            dev_dict.get('instance').set_connection('com')
            dev_dict.get('instance').set_addr(port)
            try:
                dev_dict.get('instance').connect()
            except ConnectionError as e:
                q.put(e)
            
            set_status_light(self.itlaStatus, 'idle')
            self.handle_connect(self.itlaStatus, 'ITLA5300')
            self.itlaConnection.setText("Отключить")
        else:
            dev_dict.get('instance').close()
            self.itlaConnection.setText("Подключить")
            set_status_light(self.itlaStatus, 'init')
            

    def handle_connect(self, status_widget, dev_name):
        self.dev_thread = QThread(self)
        self.dev_worker = Worker()
        
        self.dev_worker.moveToThread(self.dev_thread)
 
        self.dev_worker.message.connect(self.update_status_lamp)
        # thread.started.connect(worker.process)
        self.dev_thread.started.connect(lambda: self.dev_worker.process(status_widget, dev_name))
 
        self.dev_thread.start()

    @QtCore.pyqtSlot(object, str)
    def update_status_lamp(self, widget, status):
        set_status_light(widget, status)        
