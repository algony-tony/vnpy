# encoding: UTF-8

import os
import configparser

vtconfig = configparser.ConfigParser()
vtconfig.read(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'vtcmd.ini'))

globalSetting = vtconfig['default']


gatewayconfig = configparser.ConfigParser()
gatewayconfig.read(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'gateway.ini'))
