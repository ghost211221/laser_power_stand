import time

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable

from core.context import Context
from core.exceptions import DeviceNotFoundError, ConnectionError
from core.utils import dBm_to_mW
from core.logs.log import LoggingQueue
from itf_modules.utils import set_status_light

context = Context()
q = LoggingQueue()

class WorkerSignals(QObject):
    '''Signal for messaging device state'''
    message = pyqtSignal(str, list)
    stopped = pyqtSignal()
    finished = pyqtSignal()


class ContinuousMeasureWorker(QRunnable):
    """
    """
    def __init__(self):
        super(ContinuousMeasureWorker, self).__init__()
        self.signals = WorkerSignals()
        self.laser_name = None
        self.enabled_devices = []

    def set_laser_name(self, laser_name):
        self.laser_name = laser_name

    def set_enabled_meters(self, enabled_list):
        self.enabled_devices = enabled_list

    @property
    def devices(self):
        devices = {}
        for device in context.devices:
            if device['instance'].dev_type == 'power_meter' and device.get('enabled') and device['dev_name'] in self.enabled_devices:
                devices[device['instance'].dev_name] = device['instance']

        return devices

    @property
    def laser(self):
        if not self.laser_name:
            return

        dev_dict = context.get_device(self.laser_name)
        if not dev_dict:
            raise DeviceNotFoundError()

        return dev_dict.get('instance')

    def autoDelete(self):
        return not context.run_cont_measure

    @pyqtSlot()
    def run(self):
        while not context.exit_mode:
            if context.run_cont_measure and self.laser and self.devices:
                self.laser.set_beam_on()
                while context.run_cont_measure and not context.exit_mode:
                    print('measuring')
                    print(context.run_cont_measure)
                    for k, v in self.devices.items():
                        res = v.get_power()
                        self.signals.message.emit(k, res)
                        print(f'{k} -> {res}')
                    time.sleep(1)

                self.laser.set_beam_off()

            self.signals.stopped.emit()
            time.sleep(1)

class PowerPanHandler():

    def setup_power_pan(self, MainWindow):
        self.init_power_pan_widgets()

        self.handle_power_signals()
        self.run_cont_measure_thread()

    def init_power_pan_widgets(self):
        self.nest__powerLaserCombo()

    def nest__powerLaserCombo(self):
        """refresh list of available lasers"""
        # store previous selected
        selected = self.powerLaserCombo.currentText()

        self.powerLaserCombo.clear()
        for device in context.devices:
            if device['instance'].dev_type == 'laser' and device['instance'].status != 'init':
                self.powerLaserCombo.addItem(device['instance'].dev_name)

        # restore previous
        if selected:
            self.powerLaserCombo.setCurrentText(selected)

    def handle_power_signals(self):
        self.startPowerMeasBtn.clicked.connect(self.handle_power_meas)

    def handle_power_meas(self):
        self.set_cont_meas_state()

    @property
    def __power_selected_laser(self):
        return self.powerLaserCombo.currentText()

    @property
    def __can_start_power_meas(self):
        enabled_devices =  list(self.get_enbaled_meters__power())
        if self.__power_selected_laser:
            enabled_devices.append(self.__power_selected_laser)
        for dev_dict in context.devices:
            if not (dev_dict['dev_name'] in enabled_devices and dev_dict['instance'].connection and \
                    dev_dict['instance'].connection.connected):
                return dev_dict['dev_name']

    def get_enbaled_meters__power(self):
        enabled = []

        for widget in (self.pm2100_1_en_cb, self.pm2100_2_en_cb, self.pm2100_3_en_cb, self.pm2100_4_en_cb):
            if widget.isChecked:
                enabled.append('PM2100')
                break

        return enabled

    def set_cont_meas_state(self):
        if self.__can_start_power_meas:
            q.put(f'{self.__can_start_power_meas} is selected for process but not connected')
            return

        if context.run_laser or context.run_single_measure or context.run_scan:
            q.put(f'Can`t enable beam - measurement ia already running')
            return

        if  self.startPowerMeasBtn.text() == 'Начать измерение':
            self.startPowerMeasBtn.setText('Остановить измерение')
            context.run_cont_measure = True
            context.run_single_measure = False
            context.run_scan = False
            self._cont_power_worker.set_laser_name(self.__power_selected_laser)
            self._cont_power_worker.set_enabled_meters(self.get_enbaled_meters__power())
        else:
            context.run_cont_measure = False
            self.startPowerMeasBtn.setText('Начать измерение')


    def run_cont_measure_thread(self):
        self._cont_power_worker = ContinuousMeasureWorker() # Any other args, kwargs are passed to the run function
        self._cont_power_worker.signals.message.connect(self.update_tiles)
        self._cont_power_worker.signals.stopped.connect(self.update_power_run_btn)
        self._cont_power_worker.setAutoDelete(0)

        # Execute
        self.threadpool.start(self._cont_power_worker)

    def update_power_run_btn(self):
        self.startPowerMeasBtn.setText('Начать измерение')

    def update_tile(self, value, unitSel, widget):
        val_to_show = float(value) if unitSel.currentText() == 'dBm' else dBm_to_mW(float(value))
        widget.setValue(val_to_show)

    def update_tiles(self, dev_name, values):
        if dev_name == 'PM2100':
            if self.pm2100_1_en_cb.isChecked():
                self.update_tile(values[0], self.pm2100_1_unit_combo, self.pm2100_1_pm_spin)
            if self.pm2100_2_en_cb.isChecked():
                self.update_tile(values[1], self.pm2100_2_unit_combo, self.pm2100_2_pm_spin)
            if self.pm2100_3_en_cb.isChecked():
                self.update_tile(values[2], self.pm2100_3_unit_combo, self.pm2100_3_pm_spin)
            if self.pm2100_4_en_cb.isChecked():
                self.update_tile(values[3], self.pm2100_4_unit_combo, self.pm2100_4_pm_spin)
