from src.analyzes.abstract import AbstractAnalyze

class SingleMeas(AbstractAnalyze):
    """
    Make measure by click with selected devices
    """

    analyse_name = 'single_meas'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingleMeas, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        super().__init__()

    def run(self):
        pass

    def stop(self):
        pass
