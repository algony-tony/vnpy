# encoding: UTF-8


class C_MONGO_DB_NAME:
    # mongodb database name constant
    LOG_DB_NAME = 'VnTrader_Log_Db'
    SETTING_DB_NAME = 'VnTrader_Setting_Db'
    POSITION_DB_NAME = 'VnTrader_Position_Db'
    TICK_DB_NAME = 'VnTrader_Tick_Db'
    DAILY_DB_NAME = 'VnTrader_Daily_Db'
    MINUTE_DB_NAME = 'VnTrader_1Min_Db'


class C_EVENT:
    # Event 预定义类型
    EVENT_TIMER = 'eTimer'                  # 计时器事件，每隔1秒发送一次
    EVENT_TICK = 'eTick.'                   # TICK行情事件，可后接具体的vtSymbol
    EVENT_TRADE = 'eTrade.'                 # 成交回报事件
    EVENT_ORDER = 'eOrder.'                 # 报单回报事件
    EVENT_POSITION = 'ePosition.'           # 持仓回报事件
    EVENT_ACCOUNT = 'eAccount.'             # 账户回报事件
    EVENT_CONTRACT = 'eContract.'           # 合约基础信息回报事件
    EVENT_ERROR = 'eError.'                 # 错误回报事件
    EVENT_HISTORY = 'eHistory.'             # K线数据查询回报事件

class C_DIRECTION:
    # 方向常量
    DIRECTION_NONE = '无方向'
    DIRECTION_LONG = '多'
    DIRECTION_SHORT = '空'
    DIRECTION_UNKNOWN = '未知'
    DIRECTION_NET = '净'
    DIRECTION_SELL = '卖出'              # IB接口
    DIRECTION_COVEREDSHORT = '备兑空'    # 证券期权

class C_OFFSET:
    # 开平常量
    OFFSET_NONE = '无开平'
    OFFSET_OPEN = '开仓'
    OFFSET_CLOSE = '平仓'
    OFFSET_CLOSETODAY = '平今'
    OFFSET_CLOSEYESTERDAY = '平昨'
    OFFSET_UNKNOWN = '未知'

class C_ORDER_STATUS:
    # 状态常量
    STATUS_NOTTRADED = '未成交'
    STATUS_PARTTRADED = '部分成交'
    STATUS_ALLTRADED = '全部成交'
    STATUS_CANCELLED = '已撤销'
    STATUS_REJECTED = '拒单'
    STATUS_UNKNOWN = '未知'

class C_PRODUCT:
    # 合约类型常量
    PRODUCT_EQUITY = '股票'
    PRODUCT_FUTURES = '期货'
    PRODUCT_OPTION = '期权'
    PRODUCT_INDEX = '指数'
    PRODUCT_COMBINATION = '组合'
    PRODUCT_FOREX = '外汇'
    PRODUCT_UNKNOWN = '未知'
    PRODUCT_SPOT = '现货'
    PRODUCT_DEFER = '延期'
    PRODUCT_ETF = 'ETF'
    PRODUCT_WARRANT = '权证'
    PRODUCT_BOND = '债券'
    PRODUCT_NONE = ''

class C_PRICETYPE:
    # 价格类型常量
    PRICETYPE_LIMITPRICE = '限价'
    PRICETYPE_MARKETPRICE = '市价'
    PRICETYPE_FAK = 'FAK'
    PRICETYPE_FOK = 'FOK'

class C_OPTION:
    # 期权类型
    OPTION_CALL = '看涨期权'
    OPTION_PUT = '看跌期权'

class C_EXCHANGE:
    # 交易所类型
    EXCHANGE_SSE = 'SSE'       # 上交所
    EXCHANGE_SZSE = 'SZSE'     # 深交所
    EXCHANGE_CFFEX = 'CFFEX'   # 中金所
    EXCHANGE_SHFE = 'SHFE'     # 上期所
    EXCHANGE_CZCE = 'CZCE'     # 郑商所
    EXCHANGE_DCE = 'DCE'       # 大商所
    EXCHANGE_SGE = 'SGE'       # 上金所
    EXCHANGE_INE = 'INE'       # 国际能源交易中心
    EXCHANGE_UNKNOWN = 'UNKNOWN'# 未知交易所
    EXCHANGE_NONE = ''          # 空交易所
    EXCHANGE_HKEX = 'HKEX'      # 港交所
    EXCHANGE_HKFE = 'HKFE'      # 香港期货交易所

    EXCHANGE_SMART = 'SMART'       # IB智能路由（股票、期权）
    EXCHANGE_NYMEX = 'NYMEX'       # IB 期货
    EXCHANGE_GLOBEX = 'GLOBEX'     # CME电子交易平台
    EXCHANGE_IDEALPRO = 'IDEALPRO' # IB外汇ECN

    EXCHANGE_CME = 'CME'           # CME交易所
    EXCHANGE_ICE = 'ICE'           # ICE交易所
    EXCHANGE_LME = 'LME'           # LME交易所

    EXCHANGE_FXCM = 'FXCM'         # FXCM外汇做市商

    EXCHANGE_OKCOIN = 'OKCOIN'       # OKCOIN比特币交易所
    EXCHANGE_HUOBI = 'HUOBI'         # 火币比特币交易所
    EXCHANGE_LBANK = 'LBANK'         # LBANK比特币交易所
    EXCHANGE_ZB = 'ZB'		 # 比特币中国比特币交易所
    EXCHANGE_OKEX = 'OKEX'		 # OKEX比特币交易所
    EXCHANGE_OKEXFUTURE = 'OKEXFUTURE'		 # OKEX比特币交易所-期货
    EXCHANGE_BINANCE = "BINANCE"     # 币安比特币交易所
    EXCHANGE_BITFINEX = "BITFINEX"   # Bitfinex比特币交易所
    EXCHANGE_BITMEX = 'BITMEX'       # BitMEX比特币交易所
    EXCHANGE_FCOIN = 'FCOIN'         # FCoin比特币交易所
    EXCHANGE_BIGONE = 'BIGONE'       # BigOne比特币交易所
    EXCHANGE_COINBASE = 'COINBASE'   # Coinbase交易所
    EXCHANGE_BITHUMB = 'BITHUMB'     # Bithumb比特币交易所

class C_CURRENCY:
    # 货币类型
    CURRENCY_USD = 'USD'            # 美元
    CURRENCY_CNY = 'CNY'            # 人民币
    CURRENCY_HKD = 'HKD'            # 港币
    CURRENCY_UNKNOWN = 'UNKNOWN'    # 未知货币
    CURRENCY_NONE = ''              # 空货币

class C_GATEWAYTYPE:
    # 接口类型
    GATEWAYTYPE_EQUITY = 'equity'                   # 股票、ETF、债券
    GATEWAYTYPE_FUTURES = 'futures'                 # 期货、期权、贵金属
    GATEWAYTYPE_INTERNATIONAL = 'international'     # 外盘
    GATEWAYTYPE_BTC = 'btc'                         # 比特币
    GATEWAYTYPE_DATA = 'data'                       # 数据（非交易）

class C_INTERVAL:
    # K线周期类型
    INTERVAL_1M = '1分钟'
    INTERVAL_5M = '5分钟'
    INTERVAL_15M = '15分钟'
    INTERVAL_30M = '30分钟'
    INTERVAL_1H = '1小时'
    INTERVAL_4H = '4小时'
    INTERVAL_DAILY = '日线'
    INTERVAL_WEEKLY = '周线'

