# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtSerialPort, QtWidgets
from json import load, dump
from enum import Enum

from app import userOptions
from logger import GreenyyLogger


class GreenyyStatus(Enum):
    Failed = -1
    Disabled = 0
    Enabled = 1


class GreenyyByteOperations:
    '''
    Большое спасибо ChatGPT 2.0 за код для этого класса.
    Здесь собраны некоторые функции и константы для работы с 
    массивами байтов QByteArray.
    '''
    possiblePrefixes = [
        '0B', 'B',
        '0O', 'O',
        '0X', 'X'
    ]

    binaryInputRegEx = QtCore.QRegularExpression('(0b|B)[01]{1,8}', QtCore.QRegularExpression.CaseInsensitiveOption)
    octalInputRegEx = QtCore.QRegularExpression('(0o|O)[0-7]{1,8}', QtCore.QRegularExpression.CaseInsensitiveOption)
    decimalInputRegEx = QtCore.QRegularExpression('\d{1,3}')
    hexadecimalInputRegEx = QtCore.QRegularExpression('(0x|X)[0-9a-f]{1,2}', QtCore.QRegularExpression.CaseInsensitiveOption)

    #Конверсия QByteArray в строки форматов различных систем счисления

    @staticmethod
    def toBinary(arr: QtCore.QByteArray):
        '''
        Преобразует QByteArray в бинарный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '0b00010000 0b10111010 0b10111111'
        '''
        binary = userOptions().byteSeparator.join([bin(byte)[2:].zfill(8) for byte in arr])
        return userOptions().binaryPrefix + binary

    @staticmethod
    def toOctal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в восьмеричный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '020 272 277'
        '''
        octal = userOptions().byteSeparator.join([oct(byte)[2:].zfill(3) for byte in arr])
        return userOptions().octalPrefix + octal

    @staticmethod
    def toDecimal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в десятичный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '16 186 191'
        '''
        decimal = userOptions().byteSeparator.join([str(byte) for byte in arr])
        return decimal

    @staticmethod
    def toHexadecimal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в шестнадцатеричный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '0X10 0XBA 0XBF'
        '''
        hexadecimal = userOptions().byteSeparator.join([hex(byte)[2:].zfill(2) for byte in arr])
        return userOptions().hexadecimalPrefix + hexadecimal
    
    #Конверсия строк в QByteArray для разных систем счисления.

    @staticmethod
    def clean(data: str) -> str:
        '''
        Избавляет побитовую строку от всевозможных префиксов и
        конвертирует её в верхний регистр.
        '''
        cleansy = data.upper()
        
        for prefix in GreenyyByteOperations.possiblePrefixes:
            cleansy = cleansy.replace(prefix, '')

    @staticmethod
    def fromBinary(binary: str) -> QtCore.QByteArray:
        '''
        Преобразует бинарную строку в QByteArray.

        Например, '0B00010000 0B10111010 0B10111111' -> QByteArray(b'\\X10\\XBA\\XBF')
        '''
        binary = GreenyyByteOperations.clean(binary).replace(' ', '')
        array = QtCore.QByteArray()
        for i in range(0, len(binary), 8):
            byte = int(binary[i:i+8], 2)
            array.append(byte)
        return array

    @staticmethod
    def fromOctal(octal: str) -> QtCore.QByteArray:
        '''
        Преобразует восьмеричную строку в QByteArray.
        Например, '020 272 277' -> QByteArray(b'\\X10\\XBA\\XBF')
        '''
        octal = GreenyyByteOperations.clean(octal).replace(' ', '')
        array = QtCore.QByteArray()
        for i in range(0, len(octal), 3):
            byte = int(octal[i:i+3], 8)
            array.append(byte)
        return array

    @staticmethod
    def fromDecimal(decimal: str) -> QtCore.QByteArray:
        '''
        Преобразует десятичную строку в QByteArray.
        Например, '16 186 191' -> QByteArray(b'\\X10\\XBA\\XBF')
        '''
        decimal = decimal.replace(' ', '')
        array = QtCore.QByteArray()
        for i in range(0, len(decimal), 3):
            byte = int(decimal[i:i+3])
            array.append(byte)
        return array

    @staticmethod
    def fromHexadecimal(hexadecimal: str) -> QtCore.QByteArray:
        '''
        Преобразует шестнадцатеричную строку в QByteArray.
        Например, '0X10 0XBA 0XBF' -> QByteArray(b'\\X10\\XBA\\XBF')
        '''
        hexadecimal = GreenyyByteOperations.clean(hexadecimal).replace(' ', '')
        array = QtCore.QByteArray()
        for i in range(0, len(hexadecimal), 2):
            byte = int(hexadecimal[i:i+2], 16)
            array.append(byte)
        return array


from .device import GreenyyDevice
from .initializer import GreenyyDeviceInitializer
from .worker import GreenyyDeviceIniitializationWorker


class GreenyyDeviceManager(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.logger = GreenyyLogger('DeviceManager')
        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        self.logger.debug('Информация о портах получена')

        configFile = open('device.json', encoding='utf-8')
        self.config = load(configFile)
        configFile.close()
        self.logger.info('Загружены настройки устройств')

        self.devices = []
        self.threads = []
        self.pool = QtCore.QThreadPool()

        #self.threads = []
        #self.startDevices()
        #INITIALIZER не работает. Пока без многопотокового решения
        self.startDevicesSingleThread() #временное решение. Или постоянное...

    def __getitem__(self, address: str) -> GreenyyDevice:
        try:
            return [d for d in self.devices if (d.address == address)][0]
        except IndexError:
            raise KeyError(f'Устройства по адресу {address} не найдено')

    def startDevicesSingleThread(self):
        for deviceData in self.config:
            self.devices.append(GreenyyDevice(**deviceData))
        
    def startDevices(self):
        self.logger.info('Начата инициализация устройств (многопоточная)')

        for deviceData in self.config:
            self.startDevice(deviceData)

        for th in self.threads:
            self.logger.debug(f'Запуск инициализатора устройства: {th.d["address"]}')
            th.start()

        self.logger.debug('Выход из метода многопоточной инициализации устройств')

    def startDevice(self, deviceData):
        self.logger.debug(f'Создание инициализатора устройства: {deviceData["address"]}')
        ini = GreenyyDeviceIniitializationWorker(deviceData)
        ini.signals.result.connect(lambda d: self.devices.append(d))
        self.pool.start(ini)
