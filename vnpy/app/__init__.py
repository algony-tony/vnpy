# encoding: UTF-8

from vnpy.utility.logging_mixin import LoggingMixin

class AppEngine(LoggingMixin):
    def __init__(self):
        pass

    def initAll(self):
        raise NotImplementedError

    def startAll(self):
        raise NotImplementedError

    def stopAll(self):
        raise NotImplementedError
