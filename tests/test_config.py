
if __name__ == '__main__':
    from vnpy.config import *

    print(globalSetting.sections())
    print(vtconfig.sections())
    print(globalSetting['default'])
    print(globalSetting['default']['fontFamily'])
