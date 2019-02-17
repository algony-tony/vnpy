# encoding: UTF-8

import os
import sys
from time import sleep

from vnpy.config import gatewayconfig, globalSetting
from vnpy.gateway.ctpGateway.vnctpmd import *
from vnpy.gateway.ctpGateway.vnctptd import *
from vnpy.gatewya.ctpGateway.ctp_gateway import ctpGateway


def print_dict(d):
    """按照键值打印一个字典"""
    for key,value in d.items():
        print(key + ':' + str(value))

def simple_log(func):
    """简单装饰器用于输出函数名"""
    def wrapper(*args, **kw):
        print("*"*17)
        print(str(func.__name__))
        return func(*args, **kw)
    return wrapper


class TestTdApi(TdApi):

    @simple_log
    def __init__(self):
        """Constructor"""
        super(TestTdApi, self).__init__()

    @simple_log
    def onFrontConnected(self):
        """服务器连接"""
        pass

    @simple_log
    def onFrontDisconnected(self, n):
        """服务器断开"""
        print(n)

    @simple_log
    def onHeartBeatWarning(self, n):
        """心跳报警"""
        print(n)

    @simple_log
    def onRspError(self, error, n, last):
        """错误"""
        print_dict(error)

    @simple_log
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        print_dict(data)
        print_dict(error)
        self.brokerID = data['BrokerID']
        self.userID = data['UserID']
        self.frontID = data['FrontID']
        self.sessionID = data['SessionID']

    @simple_log
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRspQrySettlementInfo(self, data, error, n, last):
        """查询结算信息回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRspSettlementInfoConfirm(self, data, error, n, last):
        """确认结算信息回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRspQryInstrument(self, data, error, n, last):
        """查询合约回报"""
        print_dict(data)
        print_dict(error)
        print(n)
        print(last)


class TestMdApi(MdApi):
    """测试用实例"""

    @simple_log
    def __init__(self):
        """Constructor"""
        super(TestMdApi, self).__init__()

    @simple_log
    def onFrontConnected(self):
        """服务器连接"""
        pass

    @simple_log
    def onFrontDisconnected(self, n):
        """服务器断开"""
        print(n)

    @simple_log
    def onHeartBeatWarning(self, n):
        """心跳报警"""
        print(n)

    @simple_log
    def onRspError(self, error, n, last):
        """错误"""
        print_dict(error)

    @simple_log
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRspSubMarketData(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRspUnSubMarketData(self, data, error, n, last):
        """退订合约回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRtnDepthMarketData(self, data):
        """行情推送"""
        print_dict(data)

    @simple_log
    def onRspSubForQuoteRsp(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRspUnSubForQuoteRsp(self, data, error, n, last):
        """退订合约回报"""
        print_dict(data)
        print_dict(error)

    @simple_log
    def onRtnForQuoteRsp(self, data):
        """行情推送"""
        print_dict(data)


class test_ctpGateway():
    def setUp(self):
        self.loginReq = {}
        self.loginReq['UserID'] = gatewayconfig['CTP']['userID']
        self.loginReq['Password'] = gatewayconfig['CTP']['password']
        self.loginReq['BrokerID'] = gatewayconfig['CTP']['brokerID']
        self.conFileLocation = globalSetting['tempDir']
        self.MDFrontAddress = gatewayconfig['CTP']['mdAddress']
        self.TDFrontAddress = gatewayconfig['CTP']['tdAddress']


    def test_API(self):
        mdapi = TestMdApi()
        tdapi = TestTdApi()

        # 在C++环境中创建MdApi对象，传入参数是希望用来保存.con文件的地址
        print('-- MD createFtdcMdApi: ', mdapi.createFtdcMdApi(self.conFileLocation))
        sleep(0.5)
        print('-- MD registerFront: ', mdapi.registerFront(self.MDFrontAddress))
        sleep(0.5)
        print('-- MD init: ', mdapi.init())
        sleep(1)
        print('-- MD reqUserLogin: ', mdapi.reqUserLogin(self.loginReq, 1))
        sleep(1)
        print('-- MD Trading Day is: ' + str(mdapi.getTradingDay()))
        sleep(1)
        print('-- MD subscribeMarketData: ', mdapi.subscribeMarketData('rb1905'))
        sleep(5)
        print('-- MD unSubscribeMarketData: ', mdapi.unSubscribeMarketData('rb1905'))
        sleep(1)

        print('-- TD createFtdcTraderApi: ', tdapi.createFtdcTraderApi(self.conFileLocation))
        sleep(0.5)
        print('-- TD subscribePrivateTopic: ', tdapi.subscribePrivateTopic(0))
        sleep(0.5)
        print('-- TD subscribePublicTopic: ', tdapi.subscribePublicTopic(0))
        sleep(0.5)
        print('-- TD registerFront: ', tdapi.registerFront(self.TDFrontAddress))
        sleep(0.5)
        print('-- TD init: ', tdapi.init())
        sleep(1)
        print('-- TD reqUserLogin: ', tdapi.reqUserLogin(self.loginReq, 2))
        sleep(1)
        # 查询结算单
        print('-- TD reqQrySettlementInfo: ', tdapi.reqQrySettlementInfo(self.loginReq, 3))
        sleep(1)
        # 确认结算
        print('-- TD reqSettlementInfoConfirm: ', tdapi.reqSettlementInfoConfirm(self.loginReq, 4))
        sleep(1)
        print('-- TD reqQryInstrument: ', tdapi.reqQryInstrument({'InstrumentID':'rb1905'}, 5))
        sleep(1)
        print('-- TD reqUserLogout: ', tdapi.reqUserLogout({}, 6))
        sleep(1)

        print('-- MD exit: ', mdapi.exit())
        sleep(1)
        print('-- TD exit: ', tdapi.exit())
        sleep(1)

    def test_ctp(self):
        psss


if __name__ == '__main__':
    test_main = test_ctpGateway()
    test_main.setUp()
    test_main.test_API()

