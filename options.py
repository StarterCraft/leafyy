#coding=utf-8
from typing import List, Dict, Any
from json   import load, dump

from leafyy import LeafyyComponent
from leafyy import hardware


class LeafyyOptions(LeafyyComponent):
    __reserved__ = [
        'name',
        'displayName',
        'ui',
        'keys',
        'logDecodeASCII'
    ]

    defaults = {
        'logLevel': 'DEBUG',
        'logScrollMode': False,
        'logLoggers': [
            'All'
        ],
        'logDecodeASCII': [
            'All'
        ]
    }

    def __init__(self) -> None:
        super().__init__('options')

        try:
            load(open('options.json', encoding = 'utf-8'))
        except Exception as e:
            self.logger.warning(f'Загрузка настроек провалена: {e}')
            self.writeDefaults()

        self.read()

    def toDict(self):
        return {
            k: v
            for k, v in self.__dict__.items() if (
            '_' not in k and
            k not in ['name', 'displayName'] and any([
            isinstance(v, str),
            isinstance(v, int),
            isinstance(v, list),
            isinstance(v, dict)])
        )}

    def read(self):
        with open('options.json', encoding = 'utf-8') as configFile:
            configData: Dict[str, Any] = load(configFile)
            
        for key in configData.keys():
            if ('_' not in key and
                key not in self.__reserved__):
                setattr(self, key, configData[key])

        self._logDecodeASCII: List[str] = configData['logDecodeASCII']
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
    
    def get(self, key: str, default: Any) -> Any:
        return getattr(self, key, default)

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
        