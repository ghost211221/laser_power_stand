import sys
import os
import logging
from threading import queue


class Logger():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LoggingQueue, cls).__new__(cls)
        return cls.instance
        
    def __init__(self):
        # создаём формировщик логов (formatter):
        self.CLIENT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

        # Подготовка имени файла для логирования
        self.PATH = os.path.dirname(os.path.abspath(__file__))
        self.PATH = os.path.join(self.PATH, 'laser_power_meter.log')

        # создаём потоки вывода логов
        self.STREAM_HANDLER = logging.StreamHandler(sys.stderr)
        self.STREAM_HANDLER.setFormatter(self.CLIENT_FORMATTER)
        self.STREAM_HANDLER.setLevel(logging.INFO)
        # self.STREAM_HANDLER.setLevel(CONSTS["logging_level"])
        self.LOG_FILE = logging.FileHandler(self.PATH, encoding='utf8')
        self.LOG_FILE.setFormatter(self.CLIENT_FORMATTER)

        # создаём регистратор и настраиваем его
        self.LOGGER = logging.getLogger('main')
        # self.LOGGER.addHandler(self.STREAM_HANDLER)
        self.LOGGER.addHandler(self.LOG_FILE)
        # self.LOGGER.setLevel(CONSTS["logging_level"])
        self.LOGGER.setLevel(logging.INFO)


class LoggingQueue(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LoggingQueue, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.queue = queue