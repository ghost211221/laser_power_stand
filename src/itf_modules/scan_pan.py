import time

from pyqtgraph import PlotWidget, plot, mkPen

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable

from core.consts import COLORS_FOR_PLOTS
from core.context import Context
from core.exceptions import DeviceNotFoundError, ConnectionError
from core.utils import get_pm_devices
from core.logs.log import LoggingQueue


context = Context()
q = LoggingQueue()

class WorkerSignals(QObject):
    '''Signal for messaging device state'''
    message = pyqtSignal(str, float, list)
    finished = pyqtSignal()


class ScanWorker(QRunnable):
    """
    """
    def __init__(self):
        super(ScanWorker, self).__init__()
        self.signals = WorkerSignals()
        self.laser_name = None
        self.enabled_devices = []
        self.__step = None
        self.__start = None
        self.__stop = None

    def set_scan_params(self, start, stop, step=1):
        self.__step = step
        self.__start = start
        self.__stop = stop

    def set_laser_name(self, laser_name):
        self.laser_name = laser_name

    def set_enabled_meters(self, enabled_list):
        self.enabled_devices = enabled_list

    def set_step(self, step):
        self.__step = step

    def set_start(self, start):
        self.__start = start

    def set_stop(self, stop):
        self.__stop = stop

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

    @property
    def is_configured(self):
        return self.__step and self.__start and self.__stop

    def autoDelete(self):
        return not context.run_scan

    @pyqtSlot()
    def run(self):
        while not context.exit_mode:
            if context.run_scan and self.laser and self.devices:
                if self.is_configured:
                    val = self.__start
                    while context.run_scan and val <= self.__stop:
                        self.laser.set_wavelen(val)
                        self.laser.set_beam_on()
                        time.sleep(1)
                        print('measuring')
                        print(context.run_cont_measure)
                        for k, v in self.devices.items():
                            res = v.get_power()
                            self.signals.message.emit(k, val, res)
                            print(f'{k} -> {res}')

                        self.laser.set_beam_off()
                        val += self.__step
                    self.signals.finished.emit()
                    context.run_scan = False
                else:
                    q.put(f'Scan measure is not cofigured. Check that all values are set.')


            time.sleep(1)

class ScanPanHandler():
    """Device initialization panel"""

    def setup_scan_pan(self, MainWindow):
        self.scan_dev_ch_line = {}

        self.init_scan_pan_widgets()
        self.run_scan_thread()
        self.handle__scan_signals()
        self.setup_scan_plot()


    def setup_scan_plot(self):
        self.scan_graph_widget = PlotWidget()
        self.scan_graph_widget.setBackground('w')
        self.scan_graph_widget.setTitle('Сканирование')
        self.scan_graph_widget.setLabel('left', 'Мощность, dBm', color='b')
        self.scan_graph_widget.setLabel('bottom', 'Длина волны, нм', color='b')
        self.scan_graph_widget.addLegend()
        self.scan_graph_widget.showGrid(x=True, y=True)
        self.gridLayout_52.addWidget(self.scan_graph_widget, 0, 0, 1, 1)

        i = 0
        for dev in get_pm_devices():
            for ch in range(dev.chanels):
                pen = mkPen(color=COLORS_FOR_PLOTS[ch], width=2)
                line_name = f'scan_line__{dev.keys[ch]}'
                self.scan_dev_ch_line[line_name] = {
                    'line': self.scan_graph_widget.plot([], [], name=dev.labels[ch], pen=pen, symbol='+', symbolSize=10),
                    'data': {}
                }

                i += 1

    def handle__scan_signals(self):
        self.scan_pm2100_1_show_cb.stateChanged.connect(self.handle_scan__show_cb)
        self.scan_pm2100_2_show_cb.stateChanged.connect(self.handle_scan__show_cb)
        self.scan_pm2100_3_show_cb.stateChanged.connect(self.handle_scan__show_cb)
        self.scan_pm2100_4_show_cb.stateChanged.connect(self.handle_scan__show_cb)

        self.scanStartBtn.clicked.connect(self.handle_meas__scan)
        self.scanClearPlot.clicked.connect(self.handle_scan__clear_plot)

    def handle_scan__clear_plot(self):
        for line in self.scan_dev_ch_line.values():
            line['data'] = {}

        widgets = [
            self.scan_pm2100_1_show_cb,
            self.scan_pm2100_2_show_cb,
            self.scan_pm2100_3_show_cb,
            self.scan_pm2100_4_show_cb,
        ]

        for widget in widgets:
            self.handle_scan__show_widget(widget)

    def handle_scan__show_cb(self):
        self.handle_scan__show_widget(self.sender())

    def handle_scan__show_widget(self, widget):
        dev_name, ch = widget.objectName().split('_')[1:3]
        line_name = f'scan_line__{dev_name}_{int(ch)-1}'
        if widget.isChecked():
            wavelengths = list(self.scan_dev_ch_line[line_name]['data'].keys()) or []
            powers = list(self.scan_dev_ch_line[line_name]['data'].values()) or []
            self.scan_dev_ch_line[line_name]['line'].setData(wavelengths, powers)
        else:
            self.scan_dev_ch_line[line_name]['line'].setData([], [])

    def init_scan_pan_widgets(self):
        self.nest__measLaserCombo()

    def nest__scanLaserCombo(self):
        """refresh list of available lasers"""
        # store previous selected
        selected = self.scanLaserCombo.currentText()

        self.scanLaserCombo.clear()
        for device in context.devices:
            if device['instance'].dev_type == 'laser' and device['instance'].status != 'init':
                self.scanLaserCombo.addItem(device['instance'].dev_name)

        # restore previous
        if selected:
            self.scanLaserCombo.setCurrentText(selected)

    def get_enbaled_meters__scan(self):
        enabled = []

        for widget in (self.scan_pm2100_1_en_cb, self.scan_pm2100_2_en_cb, self.scan_pm2100_3_en_cb, self.scan_pm2100_4_en_cb):
            if widget.isChecked():
                enabled.append('PM2100')
                break

        return enabled

    @property
    def __scan_selected_laser(self):
        return self.scanLaserCombo.currentText()

    def handle_meas__scan(self):
        meters = self.get_enbaled_meters__scan()
        if not meters:
            q.put(f'No power meters selected for measure')
            return

        laser = self.__scan_selected_laser
        if not laser:
            q.put(f'No laser selected for measure')
            return

        step = self.scanStepSpin.value()
        if step == 0:
            q.put(f'Provide non zero step')

        start = self.scanStartSpin.value()
        stop = self.scanStopSpin.value()

        if  self.scanStartBtn.text() == 'Измерение':
            self.scanStartBtn.setText('Остановить')
            self._scan_worker.set_laser_name(laser)
            self._scan_worker.set_enabled_meters(meters)
            self._scan_worker.set_step(step)
            self._scan_worker.set_start(start)
            self._scan_worker.set_stop(stop)

            context.run_cont_measure = False
            context.run_single_measure = False
            context.run_scan = True

        else:
            context.run_scan = False
            self.scanStartBtn.setText('Измерение')

    def run_scan_thread(self):
        self._scan_worker = ScanWorker() # Any other args, kwargs are passed to the run function
        self._scan_worker.signals.message.connect(self.update_scan_plots)
        self._scan_worker.signals.finished.connect(self.update_scan_run_btn)
        self._scan_worker.setAutoDelete(0)

        # Execute
        self.threadpool.start(self._scan_worker)

    def update_scan_run_btn(self):
        self.scanStartBtn.setText('Измерение')

    def update_scan_plots(self, dev_name, key, values):
        for device in context.devices:
            if device['dev_name'] == dev_name:
                for ch in range(device['instance'].chanels):
                    line_name = f'scan_line__{dev_name.lower()}_{int(ch)}'
                    self.scan_dev_ch_line[line_name]['data'][key] = float(values[ch])

        widgets = [
            self.scan_pm2100_1_show_cb,
            self.scan_pm2100_2_show_cb,
            self.scan_pm2100_3_show_cb,
            self.scan_pm2100_4_show_cb,
        ]

        for widget in widgets:
            self.handle_scan__show_widget(widget)