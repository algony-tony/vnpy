# encoding: UTF-8

import os
import configparser
import tempfile

# General Settings
vtconfig = configparser.ConfigParser()
vtconfig.read(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'vtcmd.ini'))

if 'tempDir' not in vtconfig['default']:
    vtconfig['default']['tempDir'] = tempfile.gettempdir()

tempdir = os.path.expanduser(vtconfig.get('default','tempDir'))
if os.path.isdir(tempdir):
    vtconfig['default']['tempDir'] = tempdir
else:
    vtconfig['default']['tempDir'] = tempfile.gettempdir()


globalSetting = vtconfig['default']


# Gateway Settings
gatewayconfig = configparser.ConfigParser()
gatewayconfig.read(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'gateway.ini'))
