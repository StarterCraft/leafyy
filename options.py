from PyQt5 import QtWidgets

from json import load, dump
from glob import glob

from app import device, logging
from logger import GreenyyLogger


class GreenyyKeySequences:
    def __init__(self, keys: dict) -> None:
        self.logFolder = keys['logFolder']
        self.logScrollMode = keys['logScrollMode']
        self.logIncreaseFontSize = keys['logIncreaseFontSize']
        self.logReduceFontSize = keys['logReduceFontSize']

    def toDict(self):
        return {
            'logFolder': self.logFolder,
            'logScrollMode': self.logScrollMode,
            'logIncreaseFontSize': self.logIncreaseFontSize,
            'logReduceFontSize': self.logReduceFontSize
        }

    def setBinding(self, bindingName: str, binding: str):
        setattr(self, bindingName, binding)


class GreenyyUserOptions:
    defaults = {
        'logLevel': 'DEBUG',
        'logScrollMode': False,
        'logSources': [
            'All'
        ],
        'logDecodeASCII': [
            'All'
        ],
        'keys': {
            'logFolder': 'Ctrl+N',
            'logScrollMode': 'Ctrl+M',
            'logIncreaseFontSize': 'Ctrl+.',
            'logReduceFontSize': 'Ctrl+,'
        }
    }

    def __init__(self) -> None:
        self.logger = GreenyyLogger('UserOptions')

        try:
            load(open('options.json', encoding = 'utf-8'))
        except Exception:
            self.writeDefaults()

        self.read()

    def read(self):
        with open('options.json', encoding = 'utf-8') as configFile:
            configData = load(configFile)

        self.logLevel = configData['logLevel']
        self.logScrollMode = configData['logScrollMode']
        self._logSources = configData['logSources']
        self._logDecodeASCII = configData['logDecodeASCII']
        self.keys = GreenyyKeySequences(configData['keys'])
        self.logger.debug('Настройки программы загружены')

    def write(self):
        with open('options.json', encoding='utf-8') as configFile:
            configData = load(configFile)

        toWrite = {
            'logScrollMode': self.logScrollMode,
            'logSources': self._logSources,
            'logDecodeASCII': self._logDecodeASCII,

            'keys': self.keys.toDict()
            }
        
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
        if (self._logDecodeASCII[0]):
            return True

        return (deviceAddress in self._logDecodeASCII)
    
    def setLogDecodeASCII(self, deviceAddress: str, value: bool) -> None:
        if (self._logDecodeASCII[0] == 'All'):
            if (value):
                return
            
            if (deviceAddress == 'All'):
                self._logDecodeASCII.clear()
            else:
                self._logDecodeASCII = [d.address for d in device().devices if (
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

    def logWindowSources(self, loggerName: str) -> bool:
        if (self._logSources[0] == 'All'):
            return True

        return (loggerName in self._logSources)
    
    def setLogWindowSources(self, loggerName: str, value: bool) -> None:
        if (self._logSources[0] == 'All'):
            if (value):
                return
            
            if (loggerName == 'All'):
                self._logSources.clear()
            else:
                self._logSources = [logger.name for logger in logging().loggers]
            
            self.write()
            return
        
        if (not self._logSources):
            if (not value):
                return
            
            if (loggerName == 'All'):
                self._logSources.clear()
            else:
                self._logSources.append(loggerName)
            
            self.write()
            return
        
        if (loggerName in self._logSources):
            if (value):
                return
            
            self._logSources.remove(loggerName)
            
            self.write()
            return
        
        if (value):
            self._logSources.append(loggerName)
        
            self.write()
            return
        