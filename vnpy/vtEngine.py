# encoding: UTF-8

from __future__ import division

import shelve
import json
from copy import copy

from vnpy.vtConstant import C_EVENT
from vnpy.vtConstant import C_EXCHANGE as CEXC
from vnpy.vtConstant import C_DIRECTION as CDIR
from vnpy.vtConstant import C_OFFSET as COFF
from vnpy.vtConstant import C_ORDER_STATUS as OSTA
from vnpy.config import globalSetting
from vnpy.utility.file import getTempPath
from vnpy.utility.logging_mixin import LoggingMixin


class DataEngine(LoggingMixin):
    """数据引擎"""
    contractFilePath = getTempPath('ContractData.vt')
    contractJSONFilePath = getTempPath('ContractData.json')

    FinishedStatus = [OSTA.STATUS_ALLTRADED, OSTA.STATUS_REJECTED, OSTA.STATUS_CANCELLED]

    def __init__(self, mainEngine):
        self.log.debug('DataEngine initing...')
        self.mainEngine = mainEngine

        self.tickDict = {}
        self.contractDict = {}
        self.orderDict = {}
        self.workingOrderDict = {}  # 可撤销委托
        self.tradeDict = {}
        self.accountDict = {}
        self.positionDict = {}

        # 持仓细节相关 vtSymbol:PositionDetail
        self.detailDict = {}
        # 平今手续费惩罚的产品代码列表
        self.tdPenaltyList = globalSetting['tdPenalty']

        self.loadContracts()
        self.registerEvent()

    def registerEvent(self):
        self.mainEngine.registerEvent(C_EVENT.EVENT_TICK, self.UpdateTickDictFromEvent)
        self.mainEngine.registerEvent(C_EVENT.EVENT_CONTRACT, self.UpdateContractDictFromEvent)
        self.mainEngine.registerEvent(C_EVENT.EVENT_ORDER, self.UpdateOrderDictFromEvent)
        self.mainEngine.registerEvent(C_EVENT.EVENT_TRADE, self.UpdateTradeDictFromEvent)
        self.mainEngine.registerEvent(C_EVENT.EVENT_POSITION, self.UpdatePositionDictFromEvent)
        self.mainEngine.registerEvent(C_EVENT.EVENT_ACCOUNT, self.UpdateAccountDictFromEvent)

    def UpdateTickDictFromEvent(self, event):
        # TickData
        tick = event.dict_['data']
        self.tickDict[tick.vtSymbol] = tick

    def UpdateContractDictFromEvent(self, event):
        # ContractData
        # 使用常规代码(不包括交易所)可能导致重复
        contract = event.dict_['data']
        self.contractDict[contract.vtSymbol] = contract
        self.contractDict[contract.symbol] = contract
        self.log.debug('Contract: {con}, {com}'.format(
            con=contract.vtSymbol, com=contract.symbol
        ))

    def UpdateOrderDictFromEvent(self, event):
        # OrderData
        order = event.dict_['data']
        self.log.debug('Order:{oid}; vtSym:{sym}; Dir:{dir}; Pri:{pri}; Vol:{vol}'.format(
            oid=order.vtOrderID, sym=order.vtSymbol, dir=order.direction,
            pri=order.price, vol=order.totalVolume))
        self.orderDict[order.vtOrderID] = order
        # 移除交易完成订单
        if order.status in self.FinishedStatus:
            if order.vtOrderID in self.workingOrderDict:
                del self.workingOrderDict[order.vtOrderID]
        else:
            self.workingOrderDict[order.vtOrderID] = order

        # 更新到持仓细节中
        detail = self.getPositionDetail(order.vtSymbol)
        detail.updateOrder(order)

    def UpdateTradeDictFromEvent(self, event):
        # TradeData
        trade = event.dict_['data']
        self.log.debug('Trade:{tid}; Order:{oid}; vtSym:{sym}; Dir:{dir}; Pri:{pri}; Vol:{vol}'.format(
            tid=trade.vtTradeID, oid=trade.vtOrderID, sym=trade.vtSymbol,
            dir=trade.direction, pri=trade.price, vol=trade.volume))
        self.tradeDict[trade.vtTradeID] = trade
        # 更新到持仓细节中
        detail = self.getPositionDetail(trade.vtSymbol)
        detail.updateTrade(trade)

    def UpdatePositionDictFromEvent(self, event):
        # PositionData
        pos = event.dict_['data']
        self.log.debug('vtSym:{sym}; Dir:{dir}; Pri:{pri}; Vol:{vol}; Profit:{pro}'.format(
            sym=pos.vtSymbol, dir=pos.direction, pri=pos.price, vol=pos.position,
            pro=pos.positionProfit))
        self.positionDict[pos.vtPositionName] = pos
        detail = self.getPositionDetail(pos.vtSymbol)
        detail.updatePosition(pos)

    def UpdateAccountDictFromEvent(self, event):
        # AccountData
        acc = event.dict_['data']
        self.accountDict[acc.vtAccountID] = acc
        self.log.debug(
            ' '.join(['Acc:{acc};', '静金:{pre}', '动金:{bal};', '可用:{ava};', '手续费:{com};',
                      '占用:{mar};','平盈:{cls};', '持盈:{pos};']).format(
                          acc=acc.vtAccountID, pre=round(acc.preBalance,2),
                          bal=round(acc.balance,2), ava=round(acc.available,2),
                          com=round(acc.commission,2),mar=round(acc.margin,2),
                          cls=round(acc.closeProfit,2), pos=round(acc.positionProfit,2)))

    def getTick(self, vtSymbol):
        try:
            return self.tickDict[vtSymbol]
        except KeyError:
            return None

    def getContract(self, vtSymbol):
        self.log.debug('查询合约 {sm}'.format(sm=vtSymbol))
        try:
            return self.contractDict[vtSymbol]
        except KeyError:
            return None

    def getAllContracts(self):
        self.log.debug('查询所有合约')
        return self.contractDict.values()

    def saveContracts(self):
        self.log.debug('保存 {num} 个合约到硬盘'.format(num=len(self.contractDict)))
        with shelve.open(self.contractFilePath) as f:
            f['data'] = self.contractDict

        with open(self.contractJSONFilePath, 'w+') as f:
            f.write(json.dumps(
                [{k: v.__dict__} for k,v in self.contractDict.items()]
                ,indent=4, sort_keys=False))

    def loadContracts(self):
        self.log.debug('从硬盘读取合约')
        with shelve.open(self.contractFilePath) as f:
            if 'data' in f:
                d = f['data']
                for key, value in d.items():
                    self.contractDict[key] = value

    def getOrder(self, vtOrderID):
        self.log.debug('查询委托')
        try:
            return self.orderDict[vtOrderID]
        except KeyError:
            return None

    def getAllWorkingOrders(self):
        self.log.debug('查询所有活动委托（返回列表）')
        return self.workingOrderDict.values()

    def getAllOrders(self):
        self.log.debug('获取所有委托单')
        return self.orderDict.values()

    def getAllTrades(self):
        self.log.debug('获取所有已成交单')
        return self.tradeDict.values()

    def getAllPositions(self):
        self.log.debug('获取所有持仓')
        return self.positionDict.values()

    def getAllAccounts(self):
        self.log.debug('获取所有资金')
        return self.accountDict.values()

    def getPositionDetail(self, vtSymbol):
        if vtSymbol in self.detailDict:
            detail = self.detailDict[vtSymbol]
            self.log.debug('查询 {sm} 持仓'.format(sm=vtSymbol))
        else:
            self.log.debug('加入 {sm} 持仓'.format(sm=vtSymbol))
            contract = self.getContract(vtSymbol)
            detail = PositionDetail(vtSymbol, contract)
            self.detailDict[vtSymbol] = detail

            if contract:
                detail.exchange = contract.exchange
                # 上期所合约
                if contract.exchange == CEXC.EXCHANGE_SHFE:
                    detail.mode = detail.MODE_SHFE

                # 检查是否有平今惩罚
                for productID in self.tdPenaltyList:
                    if str(productID) in contract.symbol:
                        detail.mode = detail.MODE_TDPENALTY

        return detail

    def getAllPositionDetails(self):
        self.log.debug('查询所有本地持仓缓存细节')
        return self.detailDict.values()

    def updateOrderReq(self, req, vtOrderID):
        self.log.debug('委托请求更新')
        vtSymbol = req.vtSymbol

        detail = self.getPositionDetail(vtSymbol)
        detail.updateOrderReq(req, vtOrderID)

    def convertOrderReq(self, req):
        self.log.debug('根据规则转换委托请求')
        detail = self.detailDict.get(req.vtSymbol, None)
        if not detail:
            return [req]
        else:
            return detail.convertOrderReq(req)


class PositionDetail(LoggingMixin):
    """本地维护的持仓信息"""
    WorkingStatus = [OSTA.STATUS_UNKNOWN, OSTA.STATUS_NOTTRADED, OSTA.STATUS_PARTTRADED]

    MODE_NORMAL = 'normal'          # 普通模式
    MODE_SHFE = 'shfe'              # 上期所今昨分别平仓
    MODE_TDPENALTY = 'tdpenalty'    # 平今惩罚

    def __init__(self, vtSymbol, contract=None):
        self.vtSymbol = vtSymbol
        self.symbol = ''
        self.exchange = ''
        self.name = ''
        self.size = 1

        if contract:
            self.symbol = contract.symbol
            self.exchange = contract.exchange
            self.name = contract.name
            self.size = contract.size

        self.longPos = 0
        self.longYd = 0
        self.longTd = 0
        self.longPosFrozen = 0
        self.longYdFrozen = 0
        self.longTdFrozen = 0
        self.longPnl = 0.0
        self.longPrice = 0.0

        self.shortPos = 0
        self.shortYd = 0
        self.shortTd = 0
        self.shortPosFrozen = 0
        self.shortYdFrozen = 0
        self.shortTdFrozen = 0
        self.shortPnl = 0.0
        self.shortPrice = 0.0

        self.lastPrice = 0.0

        self.mode = self.MODE_NORMAL
        self.exchange = ''

        self.workingOrderDict = {}

    def updateTrade(self, trade):
        self.log.debug('成交更新')
        # 多头
        if trade.direction is CDIR.DIRECTION_LONG:
            # 开仓
            if trade.offset is COFF.OFFSET_OPEN:
                self.longTd += trade.volume
            # 平今
            elif trade.offset is COFF.OFFSET_CLOSETODAY:
                self.shortTd -= trade.volume
            # 平昨
            elif trade.offset is COFF.OFFSET_CLOSEYESTERDAY:
                self.shortYd -= trade.volume
            # 平仓
            elif trade.offset is COFF.OFFSET_CLOSE:
                # 上期所等同于平昨
                if self.exchange is CEXC.EXCHANGE_SHFE:
                    self.shortYd -= trade.volume
                # 非上期所，优先平今
                else:
                    self.shortTd -= trade.volume

                    if self.shortTd < 0:
                        self.shortYd += self.shortTd
                        self.shortTd = 0
        # 空头
        elif trade.direction is CDIR.DIRECTION_SHORT:
            # 开仓
            if trade.offset is COFF.OFFSET_OPEN:
                self.shortTd += trade.volume
            # 平今
            elif trade.offset is COFF.OFFSET_CLOSETODAY:
                self.longTd -= trade.volume
            # 平昨
            elif trade.offset is COFF.OFFSET_CLOSEYESTERDAY:
                self.longYd -= trade.volume
            # 平仓
            elif trade.offset is COFF.OFFSET_CLOSE:
                # 上期所等同于平昨
                if self.exchange is CEXC.EXCHANGE_SHFE:
                    self.longYd -= trade.volume
                # 非上期所，优先平今
                else:
                    self.longTd -= trade.volume

                    if self.longTd < 0:
                        self.longYd += self.longTd
                        self.longTd = 0

        # 汇总
        self.calculatePrice(trade)
        self.calculatePosition()
        self.calculatePnl()

    def updateOrder(self, order):
        self.log.debug('委托更新')
        # 将活动委托缓存下来
        if order.status in self.WorkingStatus:
            self.workingOrderDict[order.vtOrderID] = order

        # 移除缓存中已经完成的委托
        else:
            if order.vtOrderID in self.workingOrderDict:
                del self.workingOrderDict[order.vtOrderID]

        # 计算冻结
        self.calculateFrozen()

    def updatePosition(self, pos):
        self.log.debug('持仓更新')
        if pos.direction is CDIR.DIRECTION_LONG:
            self.longPos = pos.position
            self.longYd = pos.ydPosition
            self.longTd = self.longPos - self.longYd
            self.longPnl = pos.positionProfit
            self.longPrice = pos.price
        elif pos.direction is CDIR.DIRECTION_SHORT:
            self.shortPos = pos.position
            self.shortYd = pos.ydPosition
            self.shortTd = self.shortPos - self.shortYd
            self.shortPnl = pos.positionProfit
            self.shortPrice = pos.price

    def updateOrderReq(self, req, vtOrderID):
        self.log.debug('发单更新')
        order = OrderData()
        order.vtSymbol = req.vtSymbol
        order.symbol = req.symbol
        order.exchange = req.exchange
        order.offset = req.offset
        order.direction = req.direction
        order.totalVolume = req.volume

        self.workingOrderDict[vtOrderID] = order
        self.calculateFrozen()

    def updateTick(self, tick):
        self.lastPrice = tick.lastPrice
        self.calculatePnl()

    def calculatePnl(self):
        self.log.debug('计算持仓盈亏')
        self.longPnl = self.longPos * (self.lastPrice - self.longPrice) * self.size
        self.shortPnl = self.shortPos * (self.shortPrice - self.lastPrice) * self.size

    def calculatePrice(self, trade):
        self.log.debug('计算持仓均价(基于成交数据)')
        # 只有开仓会影响持仓均价
        if trade.offset == COFF.OFFSET_OPEN:
            if trade.direction == CDIR.DIRECTION_LONG:
                cost = self.longPrice * self.longPos
                cost += trade.volume * trade.price
                newPos = self.longPos + trade.volume
                if newPos:
                    self.longPrice = cost / newPos
                else:
                    self.longPrice = 0
            else:
                cost = self.shortPrice * self.shortPos
                cost += trade.volume * trade.price
                newPos = self.shortPos + trade.volume
                if newPos:
                    self.shortPrice = cost / newPos
                else:
                    self.shortPrice = 0

    def calculatePosition(self):
        self.log.debug('计算持仓情况')
        self.longPos = self.longTd + self.longYd
        self.shortPos = self.shortTd + self.shortYd

    def calculateFrozen(self):
        self.log.debug('计算冻结情况')
        self.longPosFrozen = 0
        self.longYdFrozen = 0
        self.longTdFrozen = 0
        self.shortPosFrozen = 0
        self.shortYdFrozen = 0
        self.shortTdFrozen = 0

        for order in self.workingOrderDict.values():
            # 计算剩余冻结量
            frozenVolume = order.totalVolume - order.tradedVolume

            # 多头委托
            if order.direction is CDIR.DIRECTION_LONG:
                # 平今
                if order.offset is COFF.OFFSET_CLOSETODAY:
                    self.shortTdFrozen += frozenVolume
                # 平昨
                elif order.offset is COFF.OFFSET_CLOSEYESTERDAY:
                    self.shortYdFrozen += frozenVolume
                # 平仓
                elif order.offset is COFF.OFFSET_CLOSE:
                    self.shortTdFrozen += frozenVolume

                    if self.shortTdFrozen > self.shortTd:
                        self.shortYdFrozen += (self.shortTdFrozen - self.shortTd)
                        self.shortTdFrozen = self.shortTd
            # 空头委托
            elif order.direction is CDIR.DIRECTION_SHORT:
                # 平今
                if order.offset is COFF.OFFSET_CLOSETODAY:
                    self.longTdFrozen += frozenVolume
                # 平昨
                elif order.offset is COFF.OFFSET_CLOSEYESTERDAY:
                    self.longYdFrozen += frozenVolume
                # 平仓
                elif order.offset is COFF.OFFSET_CLOSE:
                    self.longTdFrozen += frozenVolume

                    if self.longTdFrozen > self.longTd:
                        self.longYdFrozen += (self.longTdFrozen - self.longTd)
                        self.longTdFrozen = self.longTd

            # 汇总今昨冻结
            self.longPosFrozen = self.longYdFrozen + self.longTdFrozen
            self.shortPosFrozen = self.shortYdFrozen + self.shortTdFrozen

    def convertOrderReq(self, req):
        self.log.debug('转换委托请求')
        # 普通模式无需转换
        if self.mode is self.MODE_NORMAL:
            return [req]

        # 上期所模式拆分今昨，优先平今
        elif self.mode is self.MODE_SHFE:
            # 开仓无需转换
            if req.offset is COFF.OFFSET_OPEN:
                return [req]

            # 多头
            if req.direction is CDIR.DIRECTION_LONG:
                posAvailable = self.shortPos - self.shortPosFrozen
                tdAvailable = self.shortTd- self.shortTdFrozen
                ydAvailable = self.shortYd - self.shortYdFrozen
            # 空头
            else:
                posAvailable = self.longPos - self.longPosFrozen
                tdAvailable = self.longTd - self.longTdFrozen
                ydAvailable = self.longYd - self.longYdFrozen

            # 平仓量超过总可用，拒绝，返回空列表
            if req.volume > posAvailable:
                return []
            # 平仓量小于今可用，全部平今
            elif req.volume <= tdAvailable:
                req.offset = COFF.OFFSET_CLOSETODAY
                return [req]
            # 平仓量大于今可用，平今再平昨
            else:
                l = []

                if tdAvailable > 0:
                    reqTd = copy(req)
                    reqTd.offset = COFF.OFFSET_CLOSETODAY
                    reqTd.volume = tdAvailable
                    l.append(reqTd)

                reqYd = copy(req)
                reqYd.offset = COFF.OFFSET_CLOSEYESTERDAY
                reqYd.volume = req.volume - tdAvailable
                l.append(reqYd)

                return l

        # 平今惩罚模式，没有今仓则平昨，否则锁仓
        elif self.mode is self.MODE_TDPENALTY:
            # 多头
            if req.direction is CDIR.DIRECTION_LONG:
                td = self.shortTd
                ydAvailable = self.shortYd - self.shortYdFrozen
            # 空头
            else:
                td = self.longTd
                ydAvailable = self.longYd - self.longYdFrozen

            # 这里针对开仓和平仓委托均使用一套逻辑

            # 如果有今仓，则只能开仓（或锁仓）
            if td:
                req.offset = COFF.OFFSET_OPEN
                return [req]
            # 如果平仓量小于昨可用，全部平昨
            elif req.volume <= ydAvailable:
                if self.exchange is CEXC.EXCHANGE_SHFE:
                    req.offset = COFF.OFFSET_CLOSEYESTERDAY
                else:
                    req.offset = COFF.OFFSET_CLOSE
                return [req]
            # 平仓量大于昨可用，平仓再反向开仓
            else:
                l = []

                if ydAvailable > 0:
                    reqClose = copy(req)
                    if self.exchange is CEXC.EXCHANGE_SHFE:
                        reqClose.offset = COFF.OFFSET_CLOSEYESTERDAY
                    else:
                        reqClose.offset = COFF.OFFSET_CLOSE
                    reqClose.volume = ydAvailable

                    l.append(reqClose)

                reqOpen = copy(req)
                reqOpen.offset = COFF.OFFSET_OPEN
                reqOpen.volume = req.volume - ydAvailable
                l.append(reqOpen)

                return l

        # 其他情况则直接返回空
        return []
