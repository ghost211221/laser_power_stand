import threading

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable
from core.context import Context
from core.exceptions import DeviceNotFoundError, ConnectionError
from core.logs.log import LoggingQueue
from itf_modules.utils import set_status_light

context = Context()
q = LoggingQueue()

class WorkerSignals(QObject):
    '''Signal for messaging device state'''
    message = pyqtSignal(object, str)
    finished = pyqtSignal(str)
    finished_laser = pyqtSignal()


class DevInitWorker(QRunnable):
    """Device init worker
    can connect and init device
    or disconnect
    alse change status lamp and connection button
    """
    def __init__(self, lamp_widget, btn_widget, dev_name, action):
        super(DevInitWorker, self).__init__()
        
        self.lamp_widget = lamp_widget
        self.btn_widget = btn_widget
        self.dev_name = dev_name
        self.action = action
        self.signals = WorkerSignals()
        
    @pyqtSlot()
    def run(self):
        dev_dict = context.get_device(self.dev_name)
        if not dev_dict:
            raise DeviceNotFoundError()
        
        self.signals.message.emit(self.lamp_widget, 'processing')
        self.btn_widget.setEnabled(False)
        if self.action == 'connect':
            try:
                dev_dict.get('instance').connect()
            except ConnectionError as e:
                q.put(e)
                self.signals.message.emit(self.lamp_widget, 'init')
                self.btn_widget.setEnabled(True)
                return
            
            try:
                dev_dict.get('instance').init()
            except ConnectionError as e:
                q.put(e)
                self.signals.message.emit(self.lamp_widget, 'init')
                self.btn_widget.setEnabled(True)
                return
            
            self.signals.message.emit(self.lamp_widget, 'ready')
            self.btn_widget.setText('Отключить')
                
        elif self.action == 'disconnect':         
            dev_dict.get('instance').close()
            self.btn_widget.setText('Подключить')
            self.signals.message.emit(self.lamp_widget, 'init')
        else:
            raise Exception(f'Unkonown action "{self.action}". Available actions are: connect or disconnect')
        
        self.btn_widget.setEnabled(True)
        if dev_dict.get('instance').dev_type == 'laser':
            self.signals.finished_laser.emit()
            
        self.signals.finished.emit(self.dev_name)

class DevicesPanHandler():    
    """Device initialization panel"""
    
    def setup_devices_pan(self, MainWindow):
        self.init_device_pan_widgets()
        self.setUp_textEdits_with_regEx()
        
        self.handle_signals()
        
    def init_device_pan_widgets(self):
        """init panel widgets"""
        self.laserITLAComPortCombo.clear()
        for port in context.comports:
            self.laserITLAComPortCombo.addItem(port)
            
        if context.comports:
            self.itlaConnection.setEnabled(True)
            
        else:
            self.itlaConnection.setEnabled(False)
            
    def setUp_textEdits_with_regEx(self):
        # ip_port_regex = QRegExp('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d+')
        
        # self.pm2100AddrTE.setValidator(QRegExpValidator(ip_port_regex, self.pm2100AddrTE))
        self.pm2100AddrTE.setInputMask('000.000.000.000:0000')
            
    def handle_signals(self):
        self.laserITLAComPortCombo.currentIndexChanged.connect(self.handle_itla_comport_select)
        self.itlaConnection.clicked.connect(self.handle_itla_connect)
        self.pm2100Connection.clicked.connect(self.handle_pm2100_connect)
        
    def handle_itla_comport_select(self):
        self.itlaConnection.setEnabled(True)
        
    def handle_itla_connect(self):
        dev_dict = context.get_device('ITLA5300')
        if not dev_dict:
            raise DeviceNotFoundError()
        
        action = None    
        if dev_dict.get('instance').status == 'init':
            port = self.laserITLAComPortCombo.currentText()
            if not port:
                self.logTE.append(f'Can`t connect to {dev_dict.get("dev_name")}, no port provided')
                return
            
            dev_dict.get('instance').set_connection('com')
            dev_dict.get('instance').set_addr(port)
            
            action = 'connect'
        else:
            action = 'disconnect'
            
        self.handle_connect(self.itlaStatus, self.itlaConnection, 'ITLA5300', action)
        
    def handle_pm2100_connect(self):
        dev_dict = context.get_device('PM2100')
        if not dev_dict:
            raise DeviceNotFoundError()
        
        action = None
        if dev_dict.get('instance').status == 'init':
            addr = self.pm2100AddrTE.text()
            if not addr:
                self.logTE.append(f'Can`t connect to {dev_dict.get("dev_name")}, no address provided')
                return
            
            dev_dict.get('instance').set_connection('socket')
            dev_dict.get('instance').set_addr(addr)
            action = 'connect'
        else:
            action = 'disconnect'
            
        self.handle_connect(self.pm2100Status, self.pm2100Connection, 'PM2100', action)
            
    def handle_connect(self, lamp_widget, btn_widget, dev_name, action):
        worker = DevInitWorker(lamp_widget, btn_widget, dev_name, action) # Any other args, kwargs are passed to the run function
        worker.signals.message.connect(self.update_status_lamp)
        worker.signals.finished_laser.connect(self.update_laser_selects)
        worker.signals.finished.connect(self.update_devices_pars)

        # Execute
        self.threadpool.start(worker)

    def update_status_lamp(self, widget, status):
        set_status_light(widget, status)  

    def update_laser_selects(self):
        self.nest__powerLaserCombo()
        
    def update_devices_pars(self, dev_name):
        """when device inited - set wavelen and? power, depends on device"""
        dev_dict = context.get_device(dev_name)
        if not dev_dict:
            raise DeviceNotFoundError()
        
        if dev_name == 'PM2100':
            dev_dict.get('instance').set_wavelen(self.itla5300WaveLenSpin.value())
            
        if dev_name == 'ITLA5300':
            dev_dict.get('instance').set_wavelen(self.itla5300WaveLenSpin.value())
            dev_dict.get('instance').set_power(self.itla5300PowerSpin.value())
            
                
