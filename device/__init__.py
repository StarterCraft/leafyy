# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtSerialPort, QtWidgets
from logger import GreenyyLogger
from json import load, dump
from enum import Enum
import sys
import traceback


class GreenyyStatus(Enum):
    Failed = -1
    Disabled = 0
    Enabled = 1


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
