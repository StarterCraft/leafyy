#coding=utf-8
from PyQt5  import QtWidgets

from json   import load, dump

from greenyy    import GreenyyDirectDict
from greenyy    import hardware
from logger import GreenyyLogger


class GreenyyOptions:
    defaults = {
        'ui': {
            'generalWindow': {
                'onLaunch': True,
            }
        },

        'logLevel': 'DEBUG',
        'logScrollMode': False,
        'logLoggers': [
            'All'
        ],
        'logDecodeASCII': [
            'All'
        ],

        'keys': {
            'generalWindow': 'Ctrl+1',
            'logWindow': 'Ctrl+2',
            'settingsWindow': 'Ctrl+3',

            'logFolder': 'Ctrl+N',
            'logScrollMode': 'Ctrl+M',
            'logIncreaseFontSize': 'Ctrl+.',
            'logReduceFontSize': 'Ctrl+,'
        }
    }

    def __init__(self) -> None:
        self.logger = GreenyyLogger('Options')

        try:
            load(open('options.json', encoding = 'utf-8'))
        except Exception as e:
            self.logger.warning(f'failed to load due to {e}')
            self.writeDefaults()

        self.read()

    def toDict(self):
        return {
            k: (v.toDict() if (isinstance(v, GreenyyDirectDict)) else v)
            for k, v in self.__dict__.items() if (
            '_' not in k and any([
            isinstance(v, str),
            isinstance(v, int),
            isinstance(v, list),
            isinstance(v, dict),
            isinstance(v, GreenyyDirectDict)])
        )}

    def read(self):
        with open('options.json', encoding = 'utf-8') as configFile:
            configData = load(configFile)

        _keys = [
            'ui',
            'logLevel',
            'logScrollMode',
            'logLoggers',
            'logDevices'
        ]

        for key in _keys:
            setattr(self, key, configData[key])

        self._logDecodeASCII = configData['logDecodeASCII']
        self.keys = GreenyyDirectDict(**configData['keys'])
        self.logger.info('Настройки программы загружены')

    def write(self):
        with open('options.json', encoding='utf-8') as configFile:
            configData = load(configFile)

        toWrite = self.toDict()
        
        if (configData != toWrite):
            configData.update(toWrite)
            with open('options.json', 'w', encoding='utf-8') as configFile:
                dump(configData, configFile, indent = 4)
            self.logger.info('Настройки программы сохранены')

    def writeDefaults(self):
        with open('options.json', 'w', encoding='utf-8') as configFile:
            dump(self.defaults, configFile, indent = 4)
        self.logger.critical('Настройки программы по умолчанию восстановлены')

    def logDecodeASCII(self, deviceAddress: str) -> bool:
        if (self._logDecodeASCII == ['All']):
            return True

        return (deviceAddress in self._logDecodeASCII)
    
    def setLogDecodeASCII(self, deviceAddress: str, value: bool) -> None:
        if (self._logDecodeASCII == ['All']):
            if (value):
                return
            
            if (deviceAddress == 'All'):
                self._logDecodeASCII.clear()
            else:
                self._logDecodeASCII = [d.address for d in hardware() if (
                    d.address != deviceAddress)]
            
            self.write()
            return
        
        if (not self._logDecodeASCII):
            if (not value):
                return
            
            if (deviceAddress == 'All'):
                self._logDecodeASCII.clear()
            else:
                self._logDecodeASCII.append(deviceAddress)
            
            self.write()
            return
        
        if (deviceAddress in self._logDecodeASCII):
            if (value):
                return
            
            self._logDecodeASCII.remove(deviceAddress)
            
            self.write()
            return
        
        if (value):
            self._logDecodeASCII.append(deviceAddress)
        
            self.write()
            return

    def logWindowLoggers(self, loggerName: str) -> bool:
        if (self.logLoggers == ['All']):
            return True

        return (loggerName in self.logLoggers)
    
    def setLogWindowLoggers(self, loggerName: str, value: bool) -> None:
        if (loggerName == 'All'):
            if (value):
                self.logLoggers = ['All']
            else:
                self.logLoggers = []
            
            self.write()
            return
        
        if (not self.logLoggers):
            if (not value):
                return
            
            self.logLoggers.append(loggerName)
            
            self.write()
            return
        
        if (loggerName in self.logLoggers):
            if (value):
                return
            
            self.logLoggers.remove(loggerName)
            
            self.write()
            return
        
        if (value):
            self.logLoggers.append(loggerName)
        
            self.write()
            return
        
    def logWindowDevices(self, deviceAddress: str) -> bool:
        if (self.logDevices == ['All']):
            return True

        return (deviceAddress in self.logDevices)
    
    def setLogWindowDevices(self, deviceAddress: str, value: bool) -> None:
        if (deviceAddress == 'All'):
            if (value):
                self.logDevices = ['All']
            else:
                self.logDevices = []
            
            self.write()
            return
        
        if (not self.logDevices):
            if (not value):
                return
            
            self.logDevices.append(deviceAddress)
            
            self.write()
            return
        
        if (deviceAddress in self.logDevices):
            if (value):
                return
            
            self.logDevices.remove(deviceAddress)
            
            self.write()
            return
        
        if (value):
            self.logDevices.append(deviceAddress)
        
            self.write()
            return
        