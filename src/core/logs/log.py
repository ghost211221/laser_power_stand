import sys
import os
import logging
from queue import Queue


def init_log():
    # создаём формировщик логов (formatter):
    CLIENT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

    # Подготовка имени файла для логирования
    PATH = os.path.dirname(os.path.abspath(__file__))
    PATH = os.path.join(PATH, '..', '..', '..', 'laser_power_meter.log')

    # создаём потоки вывода логов
    STREAM_HANDLER = logging.StreamHandler(sys.stderr)
    STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
    STREAM_HANDLER.setLevel(logging.INFO)
    # self.STREAM_HANDLER.setLevel(CONSTS["logging_level"])
    LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
    LOG_FILE.setFormatter(CLIENT_FORMATTER)

    # создаём регистратор и настраиваем его
    LOGGER = logging.getLogger('main')
    # self.LOGGER.addHandler(self.STREAM_HANDLER)
    LOGGER.addHandler(LOG_FILE)
    LOGGER.addHandler(STREAM_HANDLER)
    # self.LOGGER.setLevel(CONSTS["logging_level"])
    LOGGER.setLevel(logging.INFO)


class LoggingQueue(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LoggingQueue, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.__queue = Queue()

    def put(self, data, timeout=None):
        self.__queue.put(data, timeout=timeout)

    def get(self, timeout=None):
        return self.__queue.get(timeout=timeout)

    