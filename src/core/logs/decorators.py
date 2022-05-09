from src.core.logs.log import Logger, LoggingQueue

class log_to_file():
    def __init__(self):
        self.logger = Logger()


    def __call__(self, func):
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)

            self.logger.LOGGER.info(f'Function {func.__name__} was called with parameters \
                {args}, {kwargs}.\nModule: {func.__module__}')
            return res
        return decorated

class log_to_queue():
    def __call__(self, func):
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)

            logging_queue = LoggingQueue()
            logging_queue.add(f'{args}\n{res}\n')
            return res
        return decorated


