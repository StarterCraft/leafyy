# -*- coding: utf-8 -*-
from PySide6 import QtCore
from enum    import Enum

from leafyy  import app, properties


class LeafyyStatus(Enum):
    Failed = -1
    Disabled = 0
    Active = 1


class LeafyyByteOperations:
    '''
    Большое спасибо ChatGPT 3.5 за код для этого класса.
    Здесь собраны некоторые функции и константы для работы с
    массивами байтов QByteArray.
    '''
    possiblePrefixes = [
        '0B', 'B', '0b', 'b',
        '0O', 'O', '0o', 'o',
        '0X', 'X', '0x', 'x'
    ]

    binaryInputRegEx = QtCore.QRegularExpression(r'((0b|0B|b|B)[01]{1,8}[ ]*)+')
    octalInputRegEx = QtCore.QRegularExpression(r'((0o|0O|o|O)[0-7]{1,8}[ ]*)+')
    decimalInputRegEx = QtCore.QRegularExpression(r'(\d{1,3}[ ]*)+')
    hexadecimalInputRegEx = QtCore.QRegularExpression(r'((0x|0X|x|X)[0-9a-f]{1,2}[ ]*)+')

    #Конверсия QByteArray в строки форматов различных систем счисления

    @staticmethod
    def toBinary(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в бинарный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '0b00010000 0b10111010 0b10111111'
        '''
        return (properties('binaryPrefix', '0b') +
            f"{properties('byteSeparator', ' ')}{properties('binaryPrefix', '0b')}"
            .join([bin(byte)[2:].zfill(8) for byte in arr]))

    @staticmethod
    def toOctal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в восьмеричный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '0o020 0o272 0o277'
        '''
        return (properties('octalPrefix', '0o') +
            f"{properties('byteSeparator', ' ')}{properties('octalPrefix', '0o')}"
            .join([oct(byte)[2:].zfill(3) for byte in arr]))

    @staticmethod
    def toDecimal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в десятичный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '16 186 191'
        '''
        return f"{properties('byteSeparator', ' ')}".join([str(byte) for byte in arr])

    @staticmethod
    def toHexadecimal(arr: QtCore.QByteArray) -> str:
        '''
        Преобразует QByteArray в шестнадцатеричный формат.
        Например, QByteArray(b'\\X10\\XBA\\XBF') -> '0x10 0xba 0xbf'
        '''
        return (properties('hexadecimalPrefix', '0x') +
            f"{properties('byteSeparator', ' ')}{properties('hexadecimalPrefix', '0x')}"
            .join([hex(byte)[2:].zfill(2) for byte in arr]))

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


class LeafyyDeviceMessage:
    pass
