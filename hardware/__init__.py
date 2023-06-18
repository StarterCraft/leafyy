# -*- coding: utf-8 -*-
from PySide6 import QtCore, QtSerialPort, QtWidgets
from json import load, dump
from enum import Enum
from typing import Iterator, List, Any

from leafyy import LeafyyComponent
from leafyy import options
from inspection import LeafyyLogger


class LeafyyStatus(Enum):
    Failed = -1
    Disabled = 0
    Active = 1
    
    
class LeafyyByteOperations:
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

    binaryInputRegEx = QtCore.QRegularExpression(r'((0b|0B|b|B)[01]{1,8}[ ]*)+')
    octalInputRegEx = QtCore.QRegularExpression(r'((0o|0O|o|O)[0-7]{1,8}[ ]*)+')
    decimalInputRegEx = QtCore.QRegularExpression(r'(\d{1,3}[ ]*)+')
    hexadecimalInputRegEx = QtCore.QRegularExpression(r'((0x|0X|x|X)[0-9a-f]{1,2}[ ]*)+')

    #Конверсия QByteArray в строки форматов различных систем счисления

    @staticmethod
    def toBinary(arr: QtCore.QByteArray):
        '''
        Преобразует QByteArray в бинарный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '0b00010000 0b10111010 0b10111111'
        '''
        binary = options().byteSeparator.join([bin(byte)[2:].zfill(8) for byte in arr])
        return options().binaryPrefix + binary

    @staticmethod
    def toOctal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в восьмеричный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '020 272 277'
        '''
        octal = options().byteSeparator.join([oct(byte)[2:].zfill(3) for byte in arr])
        return options().octalPrefix + octal

    @staticmethod
    def toDecimal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в десятичный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '16 186 191'
        '''
        decimal = options().byteSeparator.join([str(byte) for byte in arr])
        return decimal

    @staticmethod
    def toHexadecimal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в шестнадцатеричный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '0X10 0XBA 0XBF'
        '''
        hexadecimal = options().byteSeparator.join([hex(byte)[2:].zfill(2) for byte in arr])
        return options().hexadecimalPrefix + hexadecimal
    
    #Конверсия строк в QByteArray для разных систем счисления.

    @staticmethod
    def clean(data: str) -> str:
        '''
        Избавляет побитовую строку от всевозможных префиксов и
        конвертирует её в верхний регистр.
        '''
        cleansy = data.upper()
        
        for prefix in LeafyyByteOperations.possiblePrefixes:
            cleansy = cleansy.replace(prefix, '')

    @staticmethod
    def fromBinary(binary: str) -> QtCore.QByteArray:
        '''
        Преобразует бинарную строку в QByteArray.

        Например, '0B00010000 0B10111010 0B10111111' -> QByteArray(b'\\X10\\XBA\\XBF')
        '''
        binary = LeafyyByteOperations.clean(binary).replace(' ', '')
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
        octal = LeafyyByteOperations.clean(octal).replace(' ', '')
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
        hexadecimal = LeafyyByteOperations.clean(hexadecimal).replace(' ', '')
        array = QtCore.QByteArray()
        for i in range(0, len(hexadecimal), 2):
            byte = int(hexadecimal[i:i+2], 16)
            array.append(byte)
        return array


from .device import LeafyyDevice
from .initializer import LeafyyDeviceInitializer
from .worker import LeafyyDeviceInitializationWorker


class LeafyyHardware(LeafyyComponent):
    def __init__(self):
        super().__init__('hardware')

        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        self.logger.debug('Информация о портах получена')

        with open('device.json', encoding='utf-8') as configFile:
            self.config = load(configFile)

        self.logger.info('Загружены настройки устройств')

        self.devices: List[LeafyyDevice] = []
        self.threads = []
        self.pool = QtCore.QThreadPool()

        #self.threads = []
        #self.startDevices()
        #INITIALIZER не работает. Пока без многопотокового решения

    def __getitem__(self, address: str) -> LeafyyDevice:
        try:
            return [d for d in self.devices if (d.address == address)][0]
        except IndexError:
            raise KeyError(f'Устройства по адресу {address} не найдено')
        
    def __iter__(self) -> Iterator[LeafyyDevice]:
        return iter(self.devices)
    
    def __len__(self) -> int:
        return len(self.devices)
    
    def toDict(self) -> dict[str, Any]:
        return {
            'count': {
                'total': len(self),
                'active': len([1 for d in self if d.status == LeafyyStatus.Active]),
                'disabled': len([1 for d in self if d.status == LeafyyStatus.Disabled]),
                'failed': len([1 for d in self if d.status == LeafyyStatus.Failed])
            },
            'devices': [d.toDict() for d in self]
        }

    def add(self, device: LeafyyDevice):
        self.devices.append(device)

        self.logger.debug(
            f'Устройство по адресу {device.address} зарегистрировано'
        )

    def remove(self, component: LeafyyDevice | str):
        if (isinstance(component, LeafyyDevice)):
            self.devices.remove(component)

        if (isinstance(component, str)):
            self.devices.remove(self[component.name])

        self.logger.debug(
            f'Компонент {component.name} недоступен'
        )

    def startDevicesSingleThread(self):
        for deviceData in self.config:
            LeafyyDevice(**deviceData)
        
    def startDevices(self):
        self.logger.info('Начата инициализация устройств (многопоточная)')

        for deviceData in self.config:
            self.startDevice(deviceData)

        self.logger.debug('Выход из метода многопоточной инициализации устройств')

    def startDevice(self, deviceData: dict):
        self.logger.debug(f'Создание инициализатора устройства: {deviceData["address"]}')
        ini = LeafyyDeviceInitializationWorker(deviceData)
        self.logger.debug(f'Запуск инициализатора устройства: {deviceData["address"]}')
        self.pool.start(ini)
