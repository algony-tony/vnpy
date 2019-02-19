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


# Logging Settings
LOG_LEVEL = globalSetting['LogLevel']
LOG_FILE_NAME = os.path.join(
    os.path.expanduser(globalSetting['LogFolder']),
    'vnpy.log'
)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'vnpy': {
            'format': globalSetting['LogFormat'],
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'vnpy',
        },
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_NAME,
            'formatter': 'vnpy',
            'mode': 'a',
            'maxBytes': 104857600,  # 100MB
        }
    },
    'loggers': {
        'vnpy.gateway': {
            'handlers': ['logfile', 'console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'vnpy.app': {
            'handlers': ['logfile', 'console'],
            'level': LOG_LEVEL,
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['logfile', 'console'],
        'level': LOG_LEVEL,
    }
}

