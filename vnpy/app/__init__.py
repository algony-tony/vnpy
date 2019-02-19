# encoding: UTF-8

from vnpy.utility.logging_mixin import LoggingMixin

class AppEngine(LoggingMixin):
    def __init__(self):
        pass

    def stop(self):
        raise NotImplementedError
