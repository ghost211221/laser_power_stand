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

class MeasurePanHandler():    
    """Device initialization panel"""
    
    def setup_measure_pan(self, MainWindow):
        self.measure_dev_ch_line = {}
        
        self.init_meas_pan_widgets()
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
                pen = mkPen(color=COLORS_FOR_PLOTS[0], width=2)
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
        
    def handle_meas__show_cb(self):
        dev_name, ch = self.sender().objectName().split('_')[1:3]
        line_name = f'measure_line__{dev_name}_{int(ch)-1}'
        if self.sender().isChecked:
            wavelengths = self.measure_dev_ch_line[line_name]['data'].keys() or []
            powers = self.measure_dev_ch_line[line_name]['data'].values() or []
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
            
