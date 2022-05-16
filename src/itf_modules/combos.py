from src.core.context import Context

context = Context()

class CombosHandler():

    def setup_combos(self, MainWindow):
        for port in context.comports:
            self.laserITLAComTypeCombo.addItem(port)
