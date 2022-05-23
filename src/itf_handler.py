from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import QLocale, QObject, pyqtSignal, pyqtSlot, QThread

import re

from itf_modules.gui import Ui_MainWindow
from itf_modules.devices_pan import DevicesPanHandler

from core.logs.log import LoggingQueue


q = LoggingQueue()


class Worker(QObject):
    message = pyqtSignal(str)
    running = True
    
    @pyqtSlot()
    def process(self):
        while self.running:
            try:
                data = q.get(timeout=1)
                if data:
                    self.message.emit(data)
            except Exception:
                pass
                
    def start(self):
        self.running = True
        
    def stop(self):
        self.running = False

class ItfHandler(QtWidgets.QMainWindow, Ui_MainWindow, DevicesPanHandler):

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        super().__init__()

        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        
        self.__launch_queue_process()
        
        self.setup_devices_pan(self)
        
    def __launch_queue_process(self):
        self.thread = QThread(self)
        self.worker = Worker()
        self.worker.start()
        
        self.worker.moveToThread(self.thread)
 
        self.worker.message.connect(self.update_logTE)
        # thread.started.connect(worker.process)
        self.thread.started.connect(self.worker.process)
 
        self.thread.start()
 
    @QtCore.pyqtSlot(str)
    def update_logTE(self, line):
        self.logTE.append(line) 
 
    def closeEvent(self, event):
        # do stuff
        can_exit  = True
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        
        if can_exit:
            event.accept() # let the window close
        else:
            event.ignore()