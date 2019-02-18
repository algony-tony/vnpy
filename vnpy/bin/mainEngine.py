# encoding: UTF-8

from __future__ import division

import os
import shelve
from collections import OrderedDict
from datetime import datetime
from copy import copy

from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

from vnpy.vtEvent import *
from vnpy.vtEngine import DataEngine
from vnpy.config import globalSetting
from vnpy.utility.logging_mixin import LoggingMixin


class MainEngine(LoggingMixin):
    """主引擎"""
    def __init__(self, eventEngine):
        self.todayDate = datetime.now().strftime('%Y%m%d')

        # 绑定事件引擎
        self.eventEngine = eventEngine
        self.eventEngine.start()

        # 创建数据引擎
        self.dataEngine = DataEngine(self.eventEngine)

        # MongoDB数据库相关
        self.dbClient = None    # MongoDB客户端对象

        # 接口实例
        self.gatewayDict = OrderedDict()
        self.gatewayDetailList = []

        # 应用模块实例
        self.appDict = OrderedDict()
        self.appDetailList = []

        # 风控引擎实例（特殊独立对象）
        self.rmEngine = None

    def addGateway(self, gatewayModule):
        """添加底层接口"""
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
        """添加上层应用"""
        appName = appModule.appName

        self.appDict[appName] = \
                appModule.appEngine(self, self.eventEngine)

        self.__dict__[appName] = self.appDict[appName]

        d = {
            'appName': appModule.appName,
            'appDisplayName': appModule.appDisplayName,
            'appWidget': appModule.appWidget,
            'appIco': appModule.appIco
        }
        self.appDetailList.append(d)

    def getGateway(self, gatewayName):
        """获取接口"""
        if gatewayName in self.gatewayDict:
            return self.gatewayDict[gatewayName]
        else:
            self.writeLog('接口{gateway}不存在'.format(gateway=gatewayName))
            return None

    def connect(self, gatewayName):
        gateway = self.getGateway(gatewayName)
        if gateway:
            gateway.connect()
        self.dbConnect()

    def subscribe(self, subscribeReq, gatewayName):
        gateway = self.getGateway(gatewayName)
        if gateway:
            gateway.subscribe(subscribeReq)

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

        # 保存数据引擎里的合约数据到硬盘
        self.dataEngine.saveContracts()

    def writeLog(self, content):
        self.log.info(content)

    def dbConnect(self):
        """连接MongoDB数据库"""
        if not self.dbClient:
            # 读取MongoDB的设置
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

    def getApp(self, appName):
        """获取APP引擎对象"""
        return self.appDict[appName]

    def convertOrderReq(self, req):
        """转换委托请求"""
        return self.dataEngine.convertOrderReq(req)

