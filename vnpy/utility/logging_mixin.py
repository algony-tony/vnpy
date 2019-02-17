# -*- coding: utf-8 -*-
# airflow

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import logging
import logging.config

from vnpy.config import globalSetting


LOG_LEVEL = globalSetting['LogLevel']
LOG_FILE_NAME = os.path.join(
    os.path.expanduser(globalSetting['LogFolder']),
    'vnpy.log'
)

DEFAULT_LOGGING_CONFIG = {
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


logging.config.dictConfigClass(DEFAULT_LOGGING_CONFIG).configure()


class LoggingMixin(object):
    """
    Convenience super-class to have a logger configured with the class name
    """
    def __init__(self, context=None):
        self._set_context(context)

    @property
    def log(self):
        try:
            return self._log
        except AttributeError:
            self._log = logging.root.getChild(
                self.__class__.__module__ + '.' + self.__class__.__name__
            )
            return self._log

    def _set_context(self, context):
        if context is not None:
            set_context(self.log, context)


def set_context(logger, value):
    """
    Walks the tree of loggers and tries to set the context for each handler
    :param logger: logger
    :param value: value to set
    """
    _logger = logger
    while _logger:
        for handler in _logger.handlers:
            try:
                handler.set_context(value)
            except AttributeError:
                # Not all handlers need to have context passed in so we ignore
                # the error when handlers do not have set_context defined.
                pass
        if _logger.propagate is True:
            _logger = _logger.parent
        else:
            _logger = None
