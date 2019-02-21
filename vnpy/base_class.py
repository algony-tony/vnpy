# encoding: UTF-8

from datetime import datetime
from vnpy.vtConstant import C_ORDER_STATUS as OSTA
from vnpy.utility.logging_mixin import LoggingMixin


class Event(LoggingMixin):
    """事件对象, 类似 message"""
    def __init__(self, type_=None):
        # 事件类型
        self.type_ = type_
        # 字典用于保存具体的事件数据
        self.dict_ = {}


class BaseData(Object):
    """回调函数推送数据的基础类, 其他数据类继承于此"""
    def __init__(self):
        self.gatewayName = ''         # Gateway名称
        self.rawData = None           # 原始数据


class TickData(BaseData):
    """Tick行情数据类"""
    def __init__(self):
        super(TickData, self).__init__()

        # 代码相关
        self.symbol = ''              # 合约代码
        self.exchange = ''            # 交易所代码
        self.vtSymbol = ''            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码

        # 成交数据
        self.lastPrice = 0.0            # 最新成交价
        self.lastVolume = 0             # 最新成交量
        self.volume = 0                 # 今天总成交量
        self.openInterest = 0           # 持仓量
        self.time = ''                # 时间 11:20:56.5
        self.date = ''                # 日期 20151009
        self.datetime = None                    # python的datetime时间对象

        # 常规行情
        self.openPrice = 0.0            # 今日开盘价
        self.highPrice = 0.0            # 今日最高价
        self.lowPrice = 0.0             # 今日最低价
        self.preClosePrice = 0.0

        self.upperLimit = 0.0           # 涨停价
        self.lowerLimit = 0.0           # 跌停价

        # 五档行情
        self.bidPrice1 = 0.0
        self.bidPrice2 = 0.0
        self.bidPrice3 = 0.0
        self.bidPrice4 = 0.0
        self.bidPrice5 = 0.0

        self.askPrice1 = 0.0
        self.askPrice2 = 0.0
        self.askPrice3 = 0.0
        self.askPrice4 = 0.0
        self.askPrice5 = 0.0

        self.bidVolume1 = 0
        self.bidVolume2 = 0
        self.bidVolume3 = 0
        self.bidVolume4 = 0
        self.bidVolume5 = 0

        self.askVolume1 = 0
        self.askVolume2 = 0
        self.askVolume3 = 0
        self.askVolume4 = 0
        self.askVolume5 = 0

    @staticmethod
    def createFromGateway(gateway, symbol, exchange,
                          lastPrice, lastVolume,
                          highPrice, lowPrice,
                          openPrice=0.0,
                          openInterest=0,
                          upperLimit=0.0,
                          lowerLimit=0.0):
        tick = TickData()
        tick.gatewayName = gateway.gatewayName
        tick.symbol = symbol
        tick.exchange = exchange
        tick.vtSymbol = symbol + '.' + exchange

        tick.lastPrice = lastPrice
        tick.lastVolume = lastVolume
        tick.openInterest = openInterest
        tick.datetime = datetime.now()
        tick.date = tick.datetime.strftime('%Y%m%d')
        tick.time = tick.datetime.strftime('%H:%M:%S.%f')

        tick.openPrice = openPrice
        tick.highPrice = highPrice
        tick.lowPrice = lowPrice
        tick.upperLimit = upperLimit
        tick.lowerLimit = lowerLimit
        return tick


class BarData(BaseData):
    """K线数据"""
    def __init__(self):
        super(BarData, self).__init__()

        self.vtSymbol = ''        # vt系统代码
        self.symbol = ''          # 代码
        self.exchange = ''        # 交易所

        self.open = 0.0             # OHLC
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0

        self.date = ''            # bar开始的时间，日期
        self.time = ''            # 时间
        self.datetime = None                # python的datetime时间对象

        self.volume = 0             # 成交量
        self.openInterest = 0       # 持仓量
        self.interval = ''       # K线周期


class TradeData(BaseData):
    """
    成交数据类
    一般来说，一个OrderData可能对应多个TradeData：一个订单可能多次部分成交
    """
    def __init__(self):
        super(TradeData, self).__init__()

        # 代码编号相关
        self.symbol = ''              # 合约代码
        self.exchange = ''            # 交易所代码
        self.vtSymbol = ''            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码

        self.tradeID = ''  # 成交编号 gateway内部自己生成的编号
        self.vtTradeID = ''           # 成交在vt系统中的唯一编号，通常是 Gateway名.成交编号

        self.orderID = ''             # 订单编号
        self.vtOrderID = ''           # 订单在vt系统中的唯一编号，通常是 Gateway名.订单编号

        # 成交相关
        self.direction = ''          # 成交方向
        self.offset = ''             # 成交开平仓
        self.price = 0.0                # 成交价格
        self.volume = 0                 # 成交数量
        self.tradeTime = ''           # 成交时间

    @staticmethod
    def createFromGateway(gateway, symbol, exchange, tradeID, orderID, direction, tradePrice, tradeVolume):
        trade = TradeData()
        trade.gatewayName = gateway.gatewayName
        trade.symbol = symbol
        trade.exchange = exchange
        trade.vtSymbol = symbol + '.' + exchange

        trade.orderID = orderID
        trade.vtOrderID = trade.gatewayName + '.' + trade.tradeID

        trade.tradeID = tradeID
        trade.vtTradeID = trade.gatewayName + '.' + tradeID

        trade.direction = direction
        trade.price = tradePrice
        trade.volume = tradeVolume
        trade.tradeTime = datetime.now().strftime('%H:%M:%S')
        return trade

    @staticmethod
    def createFromOrderData(order,
                            tradeID,
                            tradePrice,
                            tradeVolume):  # type: (OrderData, str, float, float)->TradeData
        trade = TradeData()
        trade.gatewayName = order.gatewayName
        trade.symbol = order.symbol
        trade.vtSymbol = order.vtSymbol

        trade.orderID = order.orderID
        trade.vtOrderID = order.vtOrderID
        trade.tradeID = tradeID
        trade.vtTradeID = trade.gatewayName + '.' + tradeID
        trade.direction = order.direction
        trade.price = tradePrice
        trade.volume = tradeVolume
        trade.tradeTime = datetime.now().strftime('%H:%M:%S')
        return trade


class OrderData(BaseData):
    """订单数据类"""
    def __init__(self):
        super(OrderData, self).__init__()

        # 代码编号相关
        self.symbol = ''              # 合约代码
        self.exchange = ''            # 交易所代码
        self.vtSymbol = ''  # 索引，统一格式：f"{symbol}.{exchange}"

        self.orderID = ''             # 订单编号 gateway内部自己生成的编号
        self.vtOrderID = ''  # 索引，统一格式：f"{gatewayName}.{orderId}"

        # 报单相关
        self.direction = ''          # 报单方向
        self.offset = ''             # 报单开平仓
        self.price = 0.0                # 报单价格
        self.totalVolume = 0            # 报单总数量
        self.tradedVolume = 0           # 报单成交数量
        self.status = OSTA.STATUS_UNKNOWN             # 报单状态

        self.orderTime = ''           # 发单时间
        self.cancelTime = ''          # 撤单时间

        # CTP/LTS相关
        self.frontID = 0                # 前置机编号
        self.sessionID = 0              # 连接编号

    @staticmethod
    def createFromGateway(gateway,                          # type: Gateway
                          orderId,                          # type: str
                          symbol,                           # type: str
                          exchange,                         # type: str
                          price,                            # type: float
                          volume,                           # type: int
                          direction,                        # type: str
                          offset='',             # type: str
                          tradedVolume=0,           # type: int
                          status='未知状态',   # type: str
                          orderTime='',          # type: str
                          cancelTime='',         # type: str
                          ):                                # type: (...)->OrderData
        vtOrder = OrderData()
        vtOrder.gatewayName = gateway.gatewayName
        vtOrder.symbol = symbol
        vtOrder.exchange = exchange
        vtOrder.vtSymbol = symbol + '.' + exchange
        vtOrder.orderID = orderId
        vtOrder.vtOrderID = gateway.gatewayName + '.' + orderId

        vtOrder.direction = direction
        vtOrder.offset = offset
        vtOrder.price = price
        vtOrder.totalVolume = volume
        vtOrder.tradedVolume = tradedVolume
        vtOrder.status = status
        vtOrder.orderTime = orderTime
        vtOrder.cancelTime = cancelTime
        return vtOrder


class PositionData(BaseData):
    """持仓数据类"""
    def __init__(self):
        super(PositionData, self).__init__()

        # 代码编号相关
        self.symbol = ''              # 合约代码
        self.exchange = ''            # 交易所代码
        self.vtSymbol = ''            # 合约在vt系统中的唯一代码，合约代码.交易所代码

        # 持仓相关
        self.direction = ''           # 持仓方向
        self.position = 0               # 持仓量
        self.frozen = 0                 # 冻结数量
        self.price = 0.0                # 持仓均价
        self.vtPositionName = ''      # 持仓在vt系统中的唯一代码，通常是vtSymbol.方向
        self.ydPosition = 0             # 昨持仓
        self.positionProfit = 0.0       # 持仓盈亏

    @staticmethod
    def createFromGateway(gateway,                      # type: Gateway
                          exchange,                     # type: str
                          symbol,                       # type: str
                          direction,                    # type: str
                          position,                     # type: int
                          frozen=0,             # type: int
                          price=0.0,            # type: float
                          yestordayPosition=0,  # type: int
                          profit=0.0            # type: float
                          ):                            # type: (...)->PositionData
        vtPosition = PositionData()
        vtPosition.gatewayName = gateway.gatewayName
        vtPosition.symbol = symbol
        vtPosition.exchange = exchange
        vtPosition.vtSymbol = symbol + '.' + exchange

        vtPosition.direction = direction
        vtPosition.position = position
        vtPosition.frozen = frozen
        vtPosition.price = price
        vtPosition.vtPositionName = vtPosition.vtSymbol + '.' + direction
        vtPosition.ydPosition = yestordayPosition
        vtPosition.positionProfit = profit
        return vtPosition


class AccountData(BaseData):
    """账户数据类"""
    def __init__(self):
        super(AccountData, self).__init__()

        # 账号代码相关
        self.accountID = ''           # 账户代码
        self.vtAccountID = ''         # 账户在vt中的唯一代码，通常是 Gateway名.账户代码

        # 数值相关
        self.preBalance = 0.0           # 昨日账户结算净值
        self.balance = 0.0              # 账户净值
        self.available = 0.0            # 可用资金
        self.commission = 0.0           # 今日手续费
        self.margin = 0.0               # 保证金占用
        self.closeProfit = 0.0          # 平仓盈亏
        self.positionProfit = 0.0       # 持仓盈亏


class ContractData(BaseData):
    """合约详细信息类"""
    def __init__(self):
        super(ContractData, self).__init__()

        self.symbol = ''              # 代码
        self.exchange = ''            # 交易所代码
        self.vtSymbol = ''            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        self.name = ''               # 合约中文名

        self.productClass = ''       # 合约类型
        self.size = 0                   # 合约大小
        self.priceTick = 0.0            # 合约最小价格TICK

        # 期权相关
        self.strikePrice = 0.0          # 期权行权价
        self.underlyingSymbol = ''    # 标的物合约代码
        self.optionType = ''         # 期权类型
        self.expiryDate = ''          # 到期日

    @staticmethod
    def createFromGateway(gateway,
                          exchange,
                          symbol,
                          productClass,
                          size,
                          priceTick,
                          name=None,
                          strikePrice=0.0,
                          underlyingSymbol='',
                          optionType='',
                          expiryDate=''
                          ):
        d = ContractData()
        d.gatewayName = gateway.gatewayName
        d.symbol = symbol
        d.exchange = exchange
        d.vtSymbol = symbol + '.' + exchange
        d.productClass = productClass
        d.size = size
        d.priceTick = priceTick
        if name is None:
            d.name = d.symbol
        d.strikePrice = strikePrice
        d.underlyingSymbol = underlyingSymbol
        d.optionType = optionType
        d.expiryDate = expiryDate
        return d


class HistoryData(object):
    """K线时间序列数据"""
    def __init__(self):
        self.vtSymbol = ''    # vt系统代码
        self.symbol = ''      # 代码
        self.exchange = ''    # 交易所

        self.interval = ''   # K线时间周期
        self.queryID = ''     # 查询号
        self.barList = []               # BarData列表


class SubscribeReq(object):
    """订阅行情时传入的对象类"""
    def __init__(self):
        self.symbol = ''              # 代码
        self.exchange = ''            # 交易所

        # 以下为IB相关
        self.productClass = ''       # 合约类型
        self.currency = ''            # 合约货币
        self.expiry = ''              # 到期日
        self.strikePrice = 0.0          # 行权价
        self.optionType = ''         # 期权类型


class OrderReq(object):
    """发单时传入的对象类"""
    def __init__(self):
        self.symbol = ''              # 代码
        self.exchange = ''            # 交易所
        self.vtSymbol = ''            # VT合约代码
        self.price = 0.0                # 价格
        self.volume = 0                 # 数量

        self.priceType = ''           # 价格类型
        self.direction = ''           # 买卖
        self.offset = ''              # 开平

        # 以下为IB相关
        self.productClass = ''       # 合约类型
        self.currency = ''            # 合约货币
        self.expiry = ''              # 到期日
        self.strikePrice = 0.0          # 行权价
        self.optionType = ''         # 期权类型
        self.lastTradeDateOrContractMonth = ''   # 合约月,IB专用
        self.multiplier = ''                     # 乘数,IB专用


class CancelOrderReq(object):
    """撤单时传入的对象类"""
    def __init__(self):
        self.symbol = ''              # 代码
        self.exchange = ''            # 交易所
        self.vtSymbol = ''            # VT合约代码

        # 以下字段主要和CTP、LTS类接口相关
        self.orderID = ''             # 报单号
        self.frontID = ''             # 前置机号
        self.sessionID = ''           # 会话号


class HistoryReq(object):
    """查询历史数据时传入的对象类"""
    def __init__(self):
        self.symbol = ''              # 代码
        self.exchange = ''            # 交易所
        self.vtSymbol = ''            # VT合约代码

        self.interval = ''           # K线周期
        self.start = None                       # 起始时间datetime对象
        self.end = None                         # 结束时间datetime对象

