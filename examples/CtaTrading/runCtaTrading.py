# encoding: UTF-8

import sys
import multiprocessing
from time import sleep
from datetime import datetime, time

from vnpy.bin.mainEngine import MainEngine
from vnpy.gateway import ctpGateway
from vnpy.app import ctaStrategy


def runChildProcess():
    """子进程运行函数"""

    me = MainEngine(EventEngineSleepInterval=0.5)
    me.addGateway(ctpGateway)
    me.addApp(ctaStrategy)
    me.startAll()

    me.dataEngine.saveContracts()   # 保存合约信息到文件

    while True:
        sleep(1)

def runParentProcess():
    """父进程运行函数"""

    DAY_START = time(8, 45)         # 日盘启动和停止时间
    DAY_END = time(15, 30)

    NIGHT_START = time(20, 45)      # 夜盘启动和停止时间
    NIGHT_END = time(2, 45)

    p = None        # 子进程句柄

    while True:
        currentTime = datetime.now().time()
        recording = False

        # 判断当前处于的时间段
        if ((currentTime >= DAY_START and currentTime <= DAY_END) or
            (currentTime >= NIGHT_START) or
            (currentTime <= NIGHT_END)):
            recording = True

        # 记录时间则需要启动子进程
        if recording and p is None:
            print('启动子进程')
            p = multiprocessing.Process(target=runChildProcess)
            p.start()
            print('子进程启动成功')

        # 非记录时间则退出子进程
        if not recording and p is not None:
            print('关闭子进程')
            p.terminate()
            p.join()
            p = None
            print('子进程关闭成功')

        sleep(5)


if __name__ == '__main__':
    runChildProcess()

    # 尽管同样实现了无人值守，但强烈建议每天启动时人工检查，为自己的PNL负责
    #runParentProcess()
