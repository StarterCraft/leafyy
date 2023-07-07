# -*- coding: utf-8 -*-
from PySide6 import QtCore, QtSerialPort
from json import loads, dumps
from enum import Enum
from typing import Iterator, List, Any
from autils import fread, fwrite

from leafyy.generic import LeafyyComponent
from leafyy         import app, options

from .generic import LeafyyStatus, LeafyyByteOperations
from .device  import LeafyyDevice


class LeafyyHardware(LeafyyComponent):
    FILENAME = 'device.json'

    def __init__(self):
        super().__init__('hardware')

        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        self.logger.debug('Информация о портах получена')

        self.config = self.getConfig()

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
    
    def getConfig(self) -> list[dict]:
        return loads(fread(self.FILENAME, encoding = 'utf-8'))
    
    def writeConfig(self, config: list[dict]):
        fwrite(self.FILENAME, dumps(config))
    
    def getDevices(self) -> dict[str, Any]:
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

    def initDevices(self):
        for deviceData in self.config:
            LeafyyDevice(**deviceData)
        
    def start(self):
        for device in self:
            if (device.isEnabled):
                self.logger.debug('Пытаюсь запустить устройство в системе')
                device.start()
