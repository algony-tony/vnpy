# encoding: UTF-8

import os
import configparser
import tempfile

# General Settings
vtconfig = configparser.ConfigParser()
vtconfig.read(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'vtcmd.ini'))

try:
    vtconfig['default']['tempDir'] = \
            os.path.expanduser(vtconfig.get('default','tempDir'))
except:
    vtconfig['default']['tempDir'] = tempfile.gettempdir()

globalSetting = vtconfig['default']


# Gateway Settings
gatewayconfig = configparser.ConfigParser()
gatewayconfig.read(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'gateway.ini'))

