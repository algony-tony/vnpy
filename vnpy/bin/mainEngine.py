# encoding: UTF-8

from __future__ import division

import os
import shelve
from time import sleep
from datetime import datetime
from collections import OrderedDict
from copy import copy

from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

from vnpy.vtEngine import DataEngine
from vnpy.config import globalSetting
from vnpy.base_class import SubscribeReq
from vnpy.utility.logging_mixin import LoggingMixin
from vnpy.utility.eventEngine import EventEngine2


class MainEngine(LoggingMixin):
    """
             app...
             |^
             v|
    -----------------------------------
    |           MainEngine            |
    -----------------------------------
    ^        ^            ^           ^
    |        |            |           |
    gateway  EventEngine  dataEngine  DBConnection
    """
    def __init__(self, EventEngineSleepInterval=None):
        self.todayDate = datetime.now().strftime('%Y%m%d')

        self.eventEngine = EventEngine2(EventEngineSleepInterval)
        self.dataEngine = DataEngine(self.eventEngine)
        self.dbClient = None    # MongoDB客户端对象

        # 接口实例
        self.gatewayDict = OrderedDict()
        self.gatewayDetailList = []

        # 应用模块实例
        self.appDict = OrderedDict()
        self.appDetailList = []

        # 风控引擎实例（特殊独立对象）
        self.rmEngine = None

    def startAll(self):
        self.eventEngine.start()
        self.dbConnect()
        self.connectGateway()
        sleep(10) # 等待接口初始化
        self.runApp()

    def addGateway(self, gatewayModule):
        gatewayName = gatewayModule.gatewayName
        self.gatewayDict[gatewayName] = \
                gatewayModule.gatewayClass(self.eventEngine, gatewayName)

        if gatewayModule.gatewayQryEnabled:
            self.gatewayDict[gatewayName].setQryEnabled(gatewayModule.gatewayQryEnabled)

        d = {
            'gatewayName': gatewayModule.gatewayName,
            'gatewayDisplayName': gatewayModule.gatewayDisplayName,
            'gatewayType': gatewayModule.gatewayType
        }
        self.gatewayDetailList.append(d)

    def addApp(self, appModule):
        appName = appModule.appName
        self.appDict[appName] = \
                appModule.appEngine(self)

        self.__dict__[appName] = self.appDict[appName]

        d = {
            'appName': appModule.appName,
            'appDisplayName': appModule.appDisplayName,
        }
        self.appDetailList.append(d)

    def connectGateway(self, gatewayName=None):
        # connect all gateways if not specified
        if not gatewayName:
            for k in self.gatewayDict.keys():
                self.gatewayDict[k].connect()
        else:
            self.getGateway(gatewayName).connect()

    def runApp(self, appName=None):
        # run all apps if not specified
        if not appName:
            for k in self.appDict.keys():
                kapp = self.appDict[k]
                kapp.initAll()
                kapp.startAll()
        else:
            kapp = self.getApp(appName)
            kapp.initAll()
            kapp.startAll()

    def getGateway(self, gatewayName):
        try:
            return self.gatewayDict[gatewayName]
        except:
            self.writeLog('接口 {gateway} 不存在'.format(gateway=gatewayName))
            return None

    def getApp(self, appName):
        try:
            return self.appDict[appName]
        except:
            self.writeLog('应用 {app} 不存在'.format(app=appName))
            return None

    def registerEvent(self, type, handler):
        self.eventEngine.registerEvent(type, handler)

    def putEvent(self, type, handler):
        self.eventEngine.putEvent(type, handler)

    def subscribe(self, subscribeReq, gatewayName):
        # 待删除
        gateway = self.getGateway(gatewayName)
        if gateway:
            gateway.subscribe(subscribeReq)

    def subscribeMarketData(self, vtSymbol, currency=None, productClass=None):
        """从 gateway 订阅行情"""
        contract = self.getContract(vtSymbol)
        if contract:
            req = SubscribeReq()
            req.symbol = contract.symbol
            req.exchange = contract.exchange

            # 对于IB接口订阅行情时所需的货币和产品类型，从策略属性中获取
            if currency:
                req.currency = currency
            if productClass:
                req.productClass = productClass

            gw =  self.getGateway(contract.gatewayName)
            if gw:
                gw.subscribe(req)
        else:
            self.writeLog('合约 {vs} 行情订阅失败'.format(vs=vtSymbol))

    def sendOrder(self, orderReq, gatewayName):
        """对特定接口发单"""
        # 如果创建了风控引擎，且风控检查失败则不发单
        if self.rmEngine and not self.rmEngine.checkRisk(orderReq, gatewayName):
            return ''

        gateway = self.getGateway(gatewayName)

        if gateway:
            vtOrderID = gateway.sendOrder(orderReq)
            # 更新发出的委托请求到数据引擎中
            self.dataEngine.updateOrderReq(orderReq, vtOrderID)
            return vtOrderID
        else:
            return ''

    def cancelOrder(self, cancelOrderReq, gatewayName):
        """对特定接口撤单"""
        gateway = self.getGateway(gatewayName)
        if gateway:
            gateway.cancelOrder(cancelOrderReq)

    def qryAccount(self, gatewayName):
        """查询特定接口的账户"""
        gateway = self.getGateway(gatewayName)
        if gateway:
            gateway.qryAccount()

    def qryPosition(self, gatewayName):
        """查询特定接口的持仓"""
        gateway = self.getGateway(gatewayName)
        if gateway:
            gateway.qryPosition()

    def dbConnect(self):
        """连接MongoDB数据库"""
        if not self.dbClient:
            try:
                # 设置MongoDB操作的超时时间为0.5秒
                self.dbClient = MongoClient(globalSetting['mongoHost'], int(globalSetting['mongoPort']), serverSelectionTimeoutMS=10)

                # 调用server_info查询服务器状态，防止服务器异常并未连接成功
                self.dbClient.server_info()

                self.writeLog('MongoDB连接成功')

            except ConnectionFailure:
                self.dbClient = None
                self.writeLog('MongoDB连接失败')

    def dbInsert(self, dbName, collectionName, d):
        """向MongoDB中插入数据，d是具体数据"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.insert_one(d)
        else:
            self.writeLog('数据插入失败, MongoDB没有连接')

    def dbQuery(self, dbName, collectionName, d, sortKey='', sortDirection=ASCENDING):
        """从MongoDB中读取数据，d是查询要求，返回的是数据库查询的指针"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]

            if sortKey:
                cursor = collection.find(d).sort(sortKey, sortDirection)    # 对查询出来的数据进行排序
            else:
                cursor = collection.find(d)

            if cursor:
                return list(cursor)
            else:
                return []
        else:
            self.writeLog('数据查询失败, MongoDB没有连接')
            return []

    def dbUpdate(self, dbName, collectionName, d, flt, upsert=False):
        """向MongoDB中更新数据，d是具体数据，flt是过滤条件，upsert代表若无是否要插入"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.replace_one(flt, d, upsert)
        else:
            self.writeLog('数据更新失败, MongoDB没有连接')

    def dbDelete(self, dbName, collectionName, flt):
        """从数据库中删除数据，flt是过滤条件"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.delete_one(flt)
        else:
            self.writeLog('数据删除失败, MongoDB没有连接')

    def getTick(self, vtSymbol):
        """查询行情"""
        return self.dataEngine.getTick(vtSymbol)

    def getContract(self, vtSymbol):
        """查询合约"""
        return self.dataEngine.getContract(vtSymbol)

    def getAllContracts(self):
        """查询所有合约（返回列表）"""
        return self.dataEngine.getAllContracts()

    def getOrder(self, vtOrderID):
        """查询委托"""
        return self.dataEngine.getOrder(vtOrderID)

    def getPositionDetail(self, vtSymbol):
        """查询持仓细节"""
        return self.dataEngine.getPositionDetail(vtSymbol)

    def getAllWorkingOrders(self):
        """查询所有的活跃的委托（返回列表）"""
        return self.dataEngine.getAllWorkingOrders()

    def getAllOrders(self):
        """查询所有委托"""
        return self.dataEngine.getAllOrders()

    def getAllTrades(self):
        """查询所有成交"""
        return self.dataEngine.getAllTrades()

    def getAllAccounts(self):
        """查询所有账户"""
        return self.dataEngine.getAllAccounts()

    def getAllPositions(self):
        """查询所有持仓"""
        return self.dataEngine.getAllPositions()

    def getAllPositionDetails(self):
        """查询本地持仓缓存细节"""
        return self.dataEngine.getAllPositionDetails()

    def getAllGatewayDetails(self):
        """查询引擎中所有底层接口的信息"""
        return self.gatewayDetailList

    def getAllAppDetails(self):
        """查询引擎中所有上层应用的信息"""
        return self.appDetailList

    def convertOrderReq(self, req):
        """转换委托请求"""
        return self.dataEngine.convertOrderReq(req)

    def exit(self):
        """退出程序前调用，保证正常退出"""
        # 安全关闭所有接口
        for gateway in self.gatewayDict.values():
            gateway.close()

        # 停止事件引擎
        self.eventEngine.stop()

        # 停止上层应用引擎
        for appEngine in self.appDict.values():
            appEngine.stop()

    def writeLog(self, content):
        self.log.info(content)

