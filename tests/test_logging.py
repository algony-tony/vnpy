import unittest

from .vnpy.utility.logging_mixin import LoggingMixin

class NewLog(LoggingMixin):
    def __init__():
        self.log.info('init')

    def msgdebug():
        self.log.debug('msgdebug')

class TestLogging(unittest.TestCase, LoggingMixin):
    def setup(self):
        pass

    def test_logging(self):
        testlog = NewLog()
        testlog.msgdebug()


if __name__ == '__main__':
    unittest.main()

