import logging

from .log import LoggingQueue


log = logging.getLogger(__name__)


class log_to_file():
    def __init__(self):
        self.logger = log


    def __call__(self, func):
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)

            self.logger.info(f'Function {func.__name__} was called with parameters \
                {args}, {kwargs}.\nModule: {func.__module__}')
            return res
        return decorated

## TODO: make decorator as function with parameters
class log_to_queue():
    def __call__(self, func):
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)

            logging_queue = LoggingQueue()
            logging_queue.put(f'{args}\n{res}\n')
            return res
        return decorated


