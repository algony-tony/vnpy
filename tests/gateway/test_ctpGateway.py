
# encoding: UTF-8

import sys
import unittest

import multiprocessing
from time import sleep
from datetime import datetime, time

from vnpy.bin.mainEngine import MainEngine
from vnpy.event import EventEngine2
from vnpy.vtEvent import EVENT_LOG, EVENT_ERROR
from vnpy.vtEngine import LogEngine
from vnpy.gateway import ctpGateway
from vnpy.app import ctaStrategy
from vnpy.app.ctaStrategy.ctaBase import EVENT_CTA_LOG

class test_ctpGateway(unittest.TestCase):
    def processErrorEvent(event):
        error = event.dict_['data']
        print(u'错误代码：%s，错误信息：%s' %(error.errorID, error.errorMsg))

    def test_runChildProcess():
        """子进程运行函数"""
        print("--- runChildProcess ---")

        # 创建日志引擎
        le = LogEngine()
        le.setLogLevel(le.LEVEL_DEBUG)
        le.addConsoleHandler()
        le.addFileHandler()

        le.info(u'启动CTA策略运行子进程')

        ee = EventEngine2()
        le.info(u'事件引擎创建成功')

        me = MainEngine(ee)
        me.addGateway(ctpGateway)
        me.addApp(ctaStrategy)
        le.info(u'主引擎创建成功')

        ee.register(EVENT_LOG, le.processLogEvent)
        ee.register(EVENT_CTA_LOG, le.processLogEvent)
        ee.register(EVENT_ERROR, processErrorEvent)
        le.info(u'注册日志事件监听')

        me.connect('CTP')
        le.info(u'连接CTP接口')

        sleep(10)                       # 等待CTP接口初始化
        me.dataEngine.saveContracts()   # 保存合约信息到文件

        cta = me.getApp(ctaStrategy.appName)

        cta.loadSetting()
        le.info(u'CTA策略载入成功')

        cta.initAll()
        le.info(u'CTA策略初始化成功')

        cta.startAll()
        le.info(u'CTA策略启动成功')

        while True:
            sleep(1)


if __name__ == '__main__':
    unittest.main()

