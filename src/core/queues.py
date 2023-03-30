from queue import Queue


class TasksQueue(object):
    """Main tasks queue
    front part puts tasks to eveluate. tuple of 3 items:
        - devices (list): list of devices used in task
        - operation (string): operation to execute
        - args (list): additional parameters
    E.g.
    (['laser1',], 'connect', [])
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TasksQueue, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.__queue = Queue()

    def put(self, data, priority=1, timeout=None):
        self.__queue.put((priority, data), timeout=timeout)

    def get(self, timeout=None):
        return self.__queue.get(timeout=timeout)
    
    def clear(self):
        with self.__queue.mutex:
            self.__queue.queue.clear()