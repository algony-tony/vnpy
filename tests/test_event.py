import unittest

import sys
from datetime import datetime
from qtpy.QtCore import QCoreApplication

class TestEvent(unittest.TestCase):

    def setup(self):
        pass

    def simpletest(event):
        print(u'处理每秒触发的计时器事件：{}'.format(str(datetime.now())))

    def test_eventengine2():
        app = QCoreApplication(sys.argv)
        ee = EventEngine2()
        ee.register(EVENT_TIMER, simpletest)
        # ee.registerGeneralHandler(simpletest)
        ee.start()

        app.exec_()

if __name__ == '__main__':
    unittest.main()

