import unittest

import sys
from time import sleep
from datetime import datetime

from vnpy.vtConstant import C_EVENT
from vnpy.utility.eventEngine import EventEngine2


class TestEventEngine(unittest.TestCase):
    def setup(self):
        pass

    def SimpleRecord(self, event):
        print('Simple Event Record: {}'.format(str(datetime.now())))

    def SimpleRecordGeneral(self, event):
        print('General Event Record: {}'.format(str(datetime.now())))

    def test_eventengine2(self):
        print('---- test_eventengine2')
        ee = EventEngine2(SleepInterval=0.5)
        ee.registerEvent(C_EVENT.EVENT_TIMER, self.SimpleRecord)
        ee.registerGeneralHandler(self.SimpleRecordGeneral)
        ee.start()
        for _ in range(3):
            print('-- ', datetime.now())
            sleep(1)

        ee.unregisterEvent(C_EVENT.EVENT_TIMER, self.SimpleRecord)
        print('# unregister SimpleRecord')
        for _ in range(2):
            print('-- ', datetime.now())
            sleep(1)

        ee.unregisterGeneralHandler(self.SimpleRecordGeneral)
        print('# unregisterGeneralHandler')
        for _ in range(2):
            print('-- ', datetime.now())
            sleep(1)

        ee.stop()


if __name__ == '__main__':
    unittest.main()

