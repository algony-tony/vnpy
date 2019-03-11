# encoding: UTF-8

import multiprocessing
from time import sleep
from datetime import datetime, time

from vnpy.bin.mainEngine import MainEngine
from vnpy.gateway import ctpGateway
from vnpy.app import dataRecorder


def runChildProcess():
    """子进程运行函数"""

    me = MainEngine()
    me.addGateway(ctpGateway)
    me.addApp(dataRecorder)
    me.startAll()

    while True:
        sleep(1)

def runParentProcess():
    """父进程运行函数"""

    DAY_START = time(8, 57)         # 日盘启动和停止时间
    DAY_END = time(15, 18)
    NIGHT_START = time(20, 57)      # 夜盘启动和停止时间
    NIGHT_END = time(2, 33)

    p = None        # 子进程句柄

    while True:
        currentTime = datetime.now().time()
        recording = False

        # 判断当前处于的时间段
        if ((currentTime >= DAY_START and currentTime <= DAY_END) or
            (currentTime >= NIGHT_START) or
            (currentTime <= NIGHT_END)):
            recording = True

        # Monday:0, Sunday:6
        if ((datetime.today().weekday() == 6) or
            (datetime.today().weekday() == 5 and currentTime > NIGHT_END) or
            (datetime.today().weekday() == 0 and currentTime < DAY_START)):
            recording = False

        if recording and p is None:
            p = multiprocessing.Process(target=runChildProcess)
            p.start()

        # 非记录时间则退出子进程
        if not recording and p is not None:
            p.terminate()
            p.join()
            p = None

        sleep(60)


if __name__ == '__main__':
    # runChildProcess()
    runParentProcess()
