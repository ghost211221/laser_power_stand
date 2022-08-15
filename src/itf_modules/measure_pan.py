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
    message = pyqtSignal(str, list)
    finished = pyqtSignal()


class SingleMeasureWorker(QRunnable):
    """
    """
    def __init__(self):
        super(SingleMeasureWorker, self).__init__()
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
        return not context.run_single_measure

    @pyqtSlot()
    def run(self):
        while not context.exit_mode:
            if context.run_single_measure and self.laser and self.devices:
                self.laser.set_beam_on()
                time.sleep(1)
                print('measuring')
                print(context.run_cont_measure)
                for k, v in self.devices.items():
                    res = v.get_power()
                    self.signals.message.emit(k, res)
                    print(f'{k} -> {res}')

                self.laser.set_beam_off()
                context.run_single_measure = False

            time.sleep(1)

class MeasurePanHandler():
    """Device initialization panel"""

    def setup_measure_pan(self, MainWindow):
        self.measure_dev_ch_line = {}

        self.init_meas_pan_widgets()
        self.run_single_measure_thread()
        self.handle__measure_signals()
        self.setup_single_meas_plot()


    def setup_single_meas_plot(self):
        self.graph_widget = PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.setTitle('Разовые измерения')
        self.graph_widget.setLabel('left', 'Мощность, dBm', color='b')
        self.graph_widget.setLabel('bottom', 'Длина волны, нм', color='b')
        self.graph_widget.addLegend()
        self.graph_widget.showGrid(x=True, y=True)
        self.gridLayout_45.addWidget(self.graph_widget, 0, 0, 1, 1)

        i = 0
        for dev in get_pm_devices():
            for ch in range(dev.chanels):
                pen = mkPen(color=COLORS_FOR_PLOTS[ch], width=2)
                line_name = f'measure_line__{dev.keys[ch]}'
                self.measure_dev_ch_line[line_name] = {
                    'line': self.graph_widget.plot([], [], name=dev.labels[ch], pen=pen, symbol='+', symbolSize=10),
                    'data': {}
                }

                i += 1

    def handle__measure_signals(self):
        self.meas_pm2100_1_show_cb.stateChanged.connect(self.handle_meas__show_cb)
        self.meas_pm2100_2_show_cb.stateChanged.connect(self.handle_meas__show_cb)
        self.meas_pm2100_3_show_cb.stateChanged.connect(self.handle_meas__show_cb)
        self.meas_pm2100_4_show_cb.stateChanged.connect(self.handle_meas__show_cb)

        self.measMeasBtn.clicked.connect(self.handle_meas__measure)
        self.measClearPlotBtn.clicked.connect(self.handle_meas__clear_plot)

    def handle_meas__clear_plot(self):
        for line in self.measure_dev_ch_line.values():
            line['data'] = {}

        widgets = [
            self.meas_pm2100_1_show_cb,
            self.meas_pm2100_2_show_cb,
            self.meas_pm2100_3_show_cb,
            self.meas_pm2100_4_show_cb,
        ]

        for widget in widgets:
            self.handle_meas__show_widget(widget)

    def handle_meas__show_cb(self):
        self.handle_meas__show_widget(self.sender())

    def handle_meas__show_widget(self, widget):
        dev_name, ch = widget.objectName().split('_')[1:3]
        line_name = f'measure_line__{dev_name}_{int(ch)-1}'
        if widget.isChecked():
            wavelengths = list(self.measure_dev_ch_line[line_name]['data'].keys()) or []
            powers = list(self.measure_dev_ch_line[line_name]['data'].values()) or []
            self.measure_dev_ch_line[line_name]['line'].setData(wavelengths, powers)
        else:
            self.measure_dev_ch_line[line_name]['line'].setData([], [])

    def init_meas_pan_widgets(self):
        self.nest__measLaserCombo()

    def nest__measLaserCombo(self):
        """refresh list of available lasers"""
        # store previous selected
        selected = self.measLaserConbo.currentText()

        self.measLaserConbo.clear()
        for device in context.devices:
            if device['instance'].dev_type == 'laser' and device['instance'].status != 'init':
                self.measLaserConbo.addItem(device['instance'].dev_name)

        # restore previous
        if selected:
            self.measLaserConbo.setCurrentText(selected)

    @property
    def __single_meas_selected_laser(self):
        return self.measLaserConbo.currentText()

    @property
    def can_start_single_meas(self):
        enabled_devices =  self.get_enbaled_meters__single()
        if self.__single_meas_selected_laser:
            enabled_devices.append(self.__single_meas_selected_laser)

        # for dev_dict in context.devices:
        #     if not (dev_dict['dev_name'] in enabled_devices and dev_dict['instance'].connection and \
        #             dev_dict['instance'].connection.connected):
        #         return dev_dict['dev_name']

    def get_enbaled_meters__single(self):
        enabled = []

        for widget in (self.pm2100_1_en_cb, self.pm2100_2_en_cb, self.pm2100_3_en_cb, self.pm2100_4_en_cb):
            if widget.isChecked():
                enabled.append('PM2100')
                break

        return enabled

    def handle_meas__measure(self):
        if self.can_start_single_meas:
            q.put(f'{self.can_start_single_meas} is selected for process but not connected')
            return

        meters = self.get_enbaled_meters__single()
        if not meters:
            q.put(f'No power meters selected for measure')
            return

        laser = self.__single_meas_selected_laser
        if not laser:
            q.put(f'No laser selected for measure')
            return

        self._single_meas_worker.set_laser_name(laser)
        self._single_meas_worker.set_enabled_meters(meters)
        context.run_single_measure = True
        context.run_cont_measure = False
        context.run_scan = False

    def run_single_measure_thread(self):
        self._single_meas_worker = SingleMeasureWorker() # Any other args, kwargs are passed to the run function
        self._single_meas_worker.signals.message.connect(self.update_single_meas_plots)
        self._single_meas_worker.setAutoDelete(0)

        # Execute
        self.threadpool.start(self._single_meas_worker)

    def update_single_meas_plots(self, dev_name, values):
        wavelen = self.itla5300WaveLenSpin.value() if self.measLaserConbo.currentText() == 'ITLA5300' else self.cls561WaveLenSpin.value()
        for device in context.devices:
            if device['dev_name'] == dev_name:
                for ch in range(device['instance'].chanels):
                    line_name = f'measure_line__{dev_name.lower()}_{int(ch)}'
                    self.measure_dev_ch_line[line_name]['data'][wavelen] = float(values[ch])

        widgets = [
            self.meas_pm2100_1_show_cb,
            self.meas_pm2100_2_show_cb,
            self.meas_pm2100_3_show_cb,
            self.meas_pm2100_4_show_cb,
        ]

        for widget in widgets:
            self.handle_meas__show_widget(widget)