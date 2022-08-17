import threading

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable

from core.context import Context
from core.exceptions import DeviceNotFoundError, ConnectionError
from core.logs.log import LoggingQueue

context = Context()
q = LoggingQueue()


class DevSetUptWorker(QRunnable):
    """Sets devices parameters
    """
    def __init__(self, lamp_widget, btn_widget, dev_name, action):
        super(DevSetUptWorker, self).__init__()

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
            self.signals.finished.emit()

class ParametersPanHandler():
    """Device initialization panel"""

    def setup_parameters_pan(self, MainWindow):
        self.init_parameters_pan_widgets()
        self.setUp_textEdits_with_regEx()

        self.handle__parameters_signals()

    def init_parameters_pan_widgets(self):
        """init panel widgets"""
        self.itla5300WaveLenSpin.setMinimum(1525)
        self.itla5300WaveLenSpin.setMaximum(1612)
        self.itla5300WaveLenSpin.setValue(1525)
        self.itla5300PowerSpin.setMinimum(7.58)
        self.itla5300PowerSpin.setMaximum(56.23)
        self.itla5300PowerSpin.setValue(7.58)

    def handle__parameters_signals(self):
        self.itla5300WaveLenSpin.valueChanged.connect(self.update_itla_wavelen)
        self.itla5300WaveLenSpin.valueChanged.connect(self.update_pm2100_wavelen)
        self.itla5300PowerSpin.valueChanged.connect(self.update_itla_power)

        self.itla5300EnableBeamBtn.clicked.connect(self.handle__itla5300_beam_enable)

    def handle__itla5300_beam_enable(self):
        if context.run_cont_measure or context.run_single_measure or context.run_scan:
            q.put(f'Can`t enable beam - measurement ia already running')
            return

        context.current_wavelen = self.itla5300WaveLenSpin.value
        dev_dict = context.get_device('ITLA5300')
        if not dev_dict:
            raise DeviceNotFoundError()

        if context.run_laser:
            dev_dict.get('instance').set_beam_off()
            context.run_laser = False
            self.itla5300EnableBeamBtn.setText('Включить луч лазера')
        else:
            dev_dict.get('instance').set_beam_on()
            context.run_laser = True
            self.itla5300EnableBeamBtn.setText('Выключить луч лазера')


    def update_itla_wavelen(self):
        if context.run_cont_measure:
            q.put(f'Can`t change wavelen during measurement')
            self.itla5300WaveLenSpin = context.current_wavelen
            return

        context.current_wavelen = self.itla5300WaveLenSpin.value
        dev_dict = context.get_device('ITLA5300')
        if not dev_dict:
            raise DeviceNotFoundError()

        try:
            dev_dict.get('instance').set_wavelen(self.itla5300WaveLenSpin.value())
        except ConnectionError:
            q.put(f'Can`t set wavelen to {dev_dict.get("dev_name")}')

    def update_itla_power(self):
        if context.run_cont_measure:
            q.put(f'Can`t change power during measurement')
            self.itla5300PowerSpin = context.current_power
            return

        context.current_power = self.itla5300PowerSpin.value
        dev_dict = context.get_device('ITLA5300')
        if not dev_dict:
            raise DeviceNotFoundError()

        try:
            dev_dict.get('instance').set_power(self.itla5300PowerSpin.value())
        except ConnectionError:
            q.put(f'Can`t set wavelen to {dev_dict.get("dev_name")}')

    def update_pm2100_wavelen(self):
        if context.run_cont_measure:
            q.put(f'Can`t change wavelen during measurement')
            self.itla5300WaveLenSpin = context.current_
            return

        dev_dict = context.get_device('PM2100')
        if not dev_dict:
            raise DeviceNotFoundError()

        try:
            dev_dict.get('instance').set_wavelen(self.itla5300WaveLenSpin.value())
        except ConnectionError:
            q.put(f'Can`t set wavelen to {dev_dict.get("dev_name")}')
