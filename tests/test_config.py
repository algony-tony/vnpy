
if __name__ == '__main__':
    from vnpy.config import *

    print(vtconfig.sections())
    print(vtconfig['default'])
    print(vtconfig['default']['fontFamily'])
    print(globalSetting['tempDir'])
