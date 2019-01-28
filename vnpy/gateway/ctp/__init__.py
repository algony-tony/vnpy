# encoding: UTF-8

from __future__ import absolute_import

from .ctp_gateway import CtpGateway
from .vnctpmd import MdApi
from .vnctptd import TdApi
from .ctp_data_type import defineDict


gatewayClass = CtpGateway
gatewayName = 'CTP'
gatewayDisplayName = 'CTP'
gatewayType = 'futures'
gatewayQryEnabled = True
