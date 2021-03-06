# encoding: UTF-8

'''
本文件中包含了CTA模块中用到的一些基础设置、类和常量等。
'''

# CTA引擎中涉及的数据类定义

# 常量定义
# CTA引擎中涉及到的交易方向类型
CTAORDER_BUY = '买开'
CTAORDER_SELL = '卖平'
CTAORDER_SHORT = '卖开'
CTAORDER_COVER = '买平'

# 本地停止单状态
STOPORDER_WAITING = '等待中'
STOPORDER_CANCELLED = '已撤销'
STOPORDER_TRIGGERED = '已触发'

# 本地停止单前缀
STOPORDERPREFIX = 'CtaStopOrder.'

# 引擎类型，用于区分当前策略的运行环境
ENGINETYPE_BACKTESTING = 'backtesting'  # 回测
ENGINETYPE_TRADING = 'trading'          # 实盘


class StopOrder(object):
    """本地停止单"""

    def __init__(self):
        """Constructor"""
        self.vtSymbol = ''
        self.orderType = ''
        self.direction = ''
        self.offset = ''
        self.price = 0.0
        self.volume = 0

        self.strategy = None             # 下停止单的策略对象
        self.stopOrderID = ''  # 停止单的本地编号
        self.status = ''       # 停止单状态
