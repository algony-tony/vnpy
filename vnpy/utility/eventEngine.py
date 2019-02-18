# encoding: UTF-8

from time import sleep
from queue import Queue, Empty
from threading import Thread
from collections import defaultdict

from qtpy.QtCore import QTimer

from vnpy.vtEvent import *
from vnpy.utility.logging_mixin import LoggingMixin

# message queue models

class EventEngine(LoggingMixin):
    """
    事件驱动引擎

    变量说明
    __queue: 事件队列
    __active: 事件引擎开关
    __thread: 事件处理线程
    __timer: 计时器
    __handlers: 事件处理函数字典


    方法说明
    __run: 事件处理线程连续运行用
    __process: 处理事件, 调用注册在引擎中的监听函数
    __onTimer: 计时器固定事件间隔触发后, 向事件队列中存入计时器事件
    start: 启动引擎
    stop: 停止引擎
    register: 向引擎中注册监听函数
    unregister: 向引擎中注销监听函数
    put: 向事件队列中存入新的事件

    事件监听函数必须定义为输入参数仅为一个event对象, 即:

    函数
    def func(event)
        ...

    对象方法
    def method(self, event)
        ...

    """

    def __init__(self):
        """初始化事件引擎"""
        # event 队列
        self.__queue = Queue()

        # 处理 event 单独线程
        self.__thread = Thread(target = self.__run)

        # 事件引擎开关
        self.__active = False

        # 计时器，用于触发计时器事件
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__onTimer)

        # __handlers 保存对应的事件调用关系
        # key: 事件名
        # value: 对 key 事件进行监听的函数列表
        self.__handlers = defaultdict(list)

        # __generalHandlerss 所有事件均调用的函数列表
        self.__generalHandlers = []

    def __run(self):
        """引擎运行"""
        while self.__active == True:
            try:
                # 获取事件的阻塞时间设为1秒
                event = self.__queue.get(block = True, timeout = 1)
                self.__process(event)
            except Empty:
                pass

    def __process(self, event):
        """处理事件"""
        if event.type_ in self.__handlers:
            [handler(event) for handler in self.__handlers[event.type_]]

        if self.__generalHandlers:
            [handler(event) for handler in self.__generalHandlers]

    def __onTimer(self):
        """向事件队列中存入计时器事件"""
        event = Event(type_=EVENT_TIMER)
        self.put(event)

    def start(self, timer=True):
        """
        引擎启动
        timer：是否要启动计时器
        """
        self.__active = True
        self.__thread.start()

        # 启动计时器，计时器事件间隔默认设定为1秒
        if timer:
            self.__timer.start(1000)

    def stop(self):
        """停止引擎"""
        self.__active = False
        self.__timer.stop()

        # 等待事件处理线程退出
        self.__thread.join()

    def put(self, event):
        self.__queue.put(event)

    def register(self, type_, handler):
        # 尝试获取该事件类型对应的处理函数列表
        # 若无 defaultDict 会自动创建新的list
        handlerList = self.__handlers[type_]

        if handler not in handlerList:
            handlerList.append(handler)

    def unregister(self, type_, handler):
        try:
            self.__handlers[type_].remove(handler)
        except ValueError:
            pass

        if len(self.__handlers[type_]) == 0:
            del self.__handlers[type_]

    def registerGeneralHandler(self, handler):
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)

    def unregisterGeneralHandler(self, handler):
        # thread-safe way to remove element
        try:
            self.__generalHandlers.remove(handler)
        except ValueError:
            pass


class EventEngine2(LoggingMixin):
    """
    计时器使用python线程的事件驱动引擎
    """

    def __init__(self, SleepInterval=None):
        self.log.debug('EventEngine2 initing...')
        self.__queue = Queue()

        # 事件引擎开关
        self.__active = False

        # 事件处理线程
        self.__thread = Thread(target = self.__run)

        # 计时器, 用于触发计时器事件, 默认1秒
        self.__timer = Thread(target = self.__runTimer)
        self.__timerActive = False
        if SleepInterval is None:
            self.__timerSleep = 1
        else:
            self.__timerSleep = SleepInterval
        self.log.debug('Timer Interval {ti}s'.format(ti=self.__timerSleep))

        # __handlers 保存对应的事件调用关系
        # key: 事件名
        # value: 对 key 事件进行监听的函数列表
        self.__handlers = defaultdict(list)

        # __generalHandlerss 所有事件均调用的函数列表
        self.__generalHandlers = []

    def __run(self):
        """引擎运行"""
        while self.__active == True:
            try:
                # 获取事件的阻塞时间设为1秒
                event = self.__queue.get(block = True, timeout = 1)
                self.__process(event)
            except Empty:
                pass

    def __process(self, event):
        """处理事件"""
        if event.type_ in self.__handlers:
            [handler(event) for handler in self.__handlers[event.type_]]

        if self.__generalHandlers:
            [handler(event) for handler in self.__generalHandlers]

    def __runTimer(self):
        """运行在计时器线程中的循环函数"""
        while self.__timerActive:
            event = Event(type_=EVENT_TIMER)
            self.put(event)
            sleep(self.__timerSleep)

    def start(self, timer=True):
        """
        引擎启动
        timer：是否要启动计时器
        """
        self.log.debug('EventEngine2 start')
        self.__active = True
        self.__thread.start()
        if timer:
            self.__timerActive = True
            self.__timer.start()

    def stop(self):
        self.log.debug('EventEngine2 stop')
        self.__active = False
        self.__timerActive = False
        self.__timer.join()

        # 等待事件处理线程退出
        self.__thread.join()

    def put(self, event):
        self.__queue.put(event)

    def register(self, type_, handler):
        handlerList = self.__handlers[type_]

        if handler not in handlerList:
            handlerList.append(handler)
            self.log.debug('Register {hd} for {tp}'.format(
                hd=handler.__name__, tp=type_))

    def unregister(self, type_, handler):
        try:
            self.__handlers[type_].remove(handler)
            self.log.debug('Unregister {hd} for {tp}'.format(
                hd=handler.__name__, tp=type_))
        except ValueError:
            pass

        if len(self.__handlers[type_]) == 0:
            del self.__handlers[type_]

    def registerGeneralHandler(self, handler):
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)
            self.log.debug('Register General Handler {hd}'.format(hd=handler.__name__))

    def unregisterGeneralHandler(self, handler):
        # thread-safe way to remove element
        try:
            self.__generalHandlers.remove(handler)
            self.log.debug('Unregister General Handler {hd}'.format(hd=handler.__name__))
        except ValueError:
            pass

