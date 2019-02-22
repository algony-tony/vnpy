# encoding: UTF-8

import time

from vnpy.vtConstant import C_EVENT
from vnpy.base_class import Event
from vnpy.utility.logging_mixin import LoggingMixin


class BaseGateway(LoggingMixin):
    """
    交易接口
    在接口里 mainEngine 和 eventEngine 是可以相互替换的
    """

    def __init__(self, mainEngine, gatewayName):
        self.mainEngine = mainEngine
        self.gatewayName = gatewayName

    def onTick(self, tick):
        """市场行情推送"""
        # 通用事件
        event1 = Event(type_=C_EVENT.EVENT_TICK)
        event1.dict_['data'] = tick
        self.mainEngine.putEvent(event1)

        # 特定合约代码的事件
        event2 = Event(type_=C_EVENT.EVENT_TICK+tick.vtSymbol)
        event2.dict_['data'] = tick
        self.mainEngine.putEvent(event2)

    def onTrade(self, trade):
        """成交信息推送"""
        # 通用事件
        event1 = Event(type_=C_EVENT.EVENT_TRADE)
        event1.dict_['data'] = trade
        self.mainEngine.putEvent(event1)

        # 特定合约的成交事件
        event2 = Event(type_=C_EVENT.EVENT_TRADE+trade.vtSymbol)
        event2.dict_['data'] = trade
        self.mainEngine.putEvent(event2)

    def onOrder(self, order):
        """订单变化推送"""
        # 通用事件
        event1 = Event(type_=C_EVENT.EVENT_ORDER)
        event1.dict_['data'] = order
        self.mainEngine.putEvent(event1)

        # 特定订单编号的事件
        event2 = Event(type_=C_EVENT.EVENT_ORDER+order.vtOrderID)
        event2.dict_['data'] = order
        self.mainEngine.putEvent(event2)

    def onPosition(self, position):
        """持仓信息推送"""
        # 通用事件
        event1 = Event(type_=C_EVENT.EVENT_POSITION)
        event1.dict_['data'] = position
        self.mainEngine.putEvent(event1)

        # 特定合约代码的事件
        event2 = Event(type_=C_EVENT.EVENT_POSITION+position.vtSymbol)
        event2.dict_['data'] = position
        self.mainEngine.putEvent(event2)

    def onAccount(self, account):
        """账户信息推送"""
        # 通用事件
        event1 = Event(type_=C_EVENT.EVENT_ACCOUNT)
        event1.dict_['data'] = account
        self.mainEngine.putEvent(event1)

        # 特定合约代码的事件
        event2 = Event(type_=C_EVENT.EVENT_ACCOUNT+account.vtAccountID)
        event2.dict_['data'] = account
        self.mainEngine.putEvent(event2)

    def onError(self, error):
        self.log.info('Error ' + error)

    def onContract(self, contract):
        """合约基础信息推送"""
        # 通用事件
        event1 = Event(type_=C_EVENT.EVENT_CONTRACT)
        event1.dict_['data'] = contract
        self.mainEngine.putEvent(event1)

    def onHistory(self, history):
        """历史数据推送"""
        event = Event(C_EVENT.EVENT_HISTORY)
        event.dict_['data'] = history
        self.mainEngine.putEvent(event)

    def connect(self):
        """连接"""
        pass

    def subscribe(self, subscribeReq):
        """订阅行情"""
        pass

    def sendOrder(self, orderReq):
        """发单"""
        pass

    def cancelOrder(self, cancelOrderReq):
        """撤单"""
        pass

    def qryAccount(self):
        """查询账户资金"""
        pass

    def qryPosition(self):
        """查询持仓"""
        pass

    def qryHistory(self, historyReq):
        """查询历史"""
        pass

    def close(self):
        """关闭"""
        pass

