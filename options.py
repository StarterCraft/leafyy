from json import load, dump

from app import device
from logger import GreenyyLogger


class GreenyyKeySequences:
    def __init__(self, keys: dict) -> None:
        self.logFolder = keys['logFolder']
        self.logWindowScrollMode = keys['logWindowScrollMode']
        self.logIncreaseFontSize = keys['logIncreaseFontSize']
        self.logReduceFontSize = keys['logReduceFontSize']

    def toDict(self):
        return {
            'logFolder': self.logFolder,
            'logWindowScrollMode': self.logWindowScrollMode,
            'logIncreaseFontSize': self.logIncreaseFontSize,
            'logReduceFontSize': self.logReduceFontSize
        }


class GreenyyUserOptions:
    def __init__(self) -> None:
        self.logger = GreenyyLogger('UserOptions')
        self.readConfig()

    def readConfig(self):
        configFile = open('options.json', encoding='utf-8')
        configData = load(configFile)
        self.logWindowScrollMode = configData['logWindowScrollMode']
        self._logWindowSources = configData['logWindowShowLoggers']
        self._logWindowDecodeASCII = configData['logWindowDecodeASCII']
        self.keys = GreenyyKeySequences(configData['keys'])
        configFile.close()
        self.logger.debug('Настройки программы загружены')

    def writeConfig(self):
        configFile = open('options.json', encoding='utf-8')
        configData = load(configFile)
        configFile.close()

        toWrite = {
            'logWindowScrollMode': self.logWindowScrollMode,
            'logWindowShowLoggers': self._logWindowSources,
            'logWindowDecodeASCII': self._logWindowDecodeASCII,

            'keys': self.keys.toDict()
            }
        
        configData.update(toWrite)
        configFile = open('options.json', 'w', encoding='utf-8')
        dump(configData, configFile)
        configFile.close()
        self.logger.debug('Настройки программы сохранены')

    def logWindowDecodeASCII(self, deviceAddress: str) -> bool:
        if (self._logWindowDecodeASCII[0] == 'All'):
            return True

        return (deviceAddress in self._logWindowDecodeASCII)
    
    def setLogWindowDecodeASCII(self, deviceAddress: str, value: bool) -> None:
        if (value and self._logWindowDecodeASCII[0] == 'All'):
            return
        
        if (self._logWindowDecodeASCII == 'All'):
            self._logWindowDecodeASCII = [d.address for d in device().devices]
            self._logWindowDecodeASCII.remove(deviceAddress)

            self.writeConfig()
            return
        
        if (deviceAddress in self._logWindowDecodeASCII):
            if (value): 
                return

            self._logWindowDecodeASCII.remove(deviceAddress)

            self.writeConfig()
            return
        
        if (value):
            self._logWindowDecodeASCII.append(deviceAddress)

            self.writeConfig()
            return
        
    def logWindowSources(self, loggerName: str) -> bool:
        if (self._logWindowSources[0] == 'All'):
            return True

        return (loggerName in self._logWindowSources)
    
    def setLogWindowSources(self, loggerName: str, value: bool) -> None:
        if (value and self._logWindowSources[0] == 'All'):
            return
        
        if (self._logWindowSources == 'All'):
            self._logWindowSources = [d.address for d in device().devices]
            self._logWindowSources.remove(loggerName)

            self.writeConfig()
            return
        
        if (loggerName in self._logWindowSources):
            if (value): 
                return

            self._logWindowSources.remove(loggerName)

            self.writeConfig()
            return
        
        if (value):
            self._logWindowSources.append(loggerName)

            self.writeConfig()
            return
