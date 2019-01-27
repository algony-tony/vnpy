# encoding: UTF-8

import json
import os


from vnpy.config import globalSetting
if globalSetting['language'].lower() == 'english':
    from .English import text, constant
else:
    from .Chinese import text, constant

