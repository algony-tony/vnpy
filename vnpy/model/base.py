# -*- coding: utf-8 -*-

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from vnpy.config import globalSetting

SQL_ALCHEMY_SETTING_SCHEMA = globalSetting['sql_alchemy_setting_schema']
SQL_ALCHEMY_POSITION_SCHEMA = globalSetting['sql_alchemy_position_schema']
SQL_ALCHEMY_DATA_SCHEMA = globalSetting['sql_alchemy_data_schema']

if not SQL_ALCHEMY_SETTING_SCHEMA or SQL_ALCHEMY_SETTING_SCHEMA.isspace():
    BaseSetting = declarative_base()
else:
    BaseSetting = declarative_base(metadata=MetaData(schema=SQL_ALCHEMY_SETTING_SCHEMA))

if not SQL_ALCHEMY_POSITION_SCHEMA or SQL_ALCHEMY_POSITION_SCHEMA.isspace():
    BasePosition = declarative_base()
else:
    BasePosition = declarative_base(metadata=MetaData(schema=SQL_ALCHEMY_POSITION_SCHEMA))

if not SQL_ALCHEMY_DATA_SCHEMA or SQL_ALCHEMY_DATA_SCHEMA.isspace():
    BaseData = declarative_base()
else:
    BaseData = declarative_base(metadata=MetaData(schema=SQL_ALCHEMY_DATA_SCHEMA))
