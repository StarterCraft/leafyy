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
    configFileName = 'device.json'
    devices: List[LeafyyDevice] = []

    def __init__(self):
        super().__init__('hardware')

        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        self.logger.debug('Информация о портах получена')

        self.config = self.getConfig()

        self.logger.info('Загружены настройки устройств')

        self.threads = []
        self.pool = QtCore.QThreadPool()

        #self.threads = []
        #self.startDevices()
        #INITIALIZER не работает. Пока без многопотокового решения

    def __getitem__(self, key: int | str) -> LeafyyDevice:
        if (isinstance(key, str)):
            try:
                return [d for d in self.devices if (d.address == key)][0]
            except IndexError as e:
                raise KeyError(f'Устройства по адресу {key} не найдено') from e
            
        else:
            return self.devices[key]
        
    def __iter__(self) -> Iterator[LeafyyDevice]:
        return iter(self.devices)
    
    def __len__(self) -> int:
        return len(self.devices)
    
    def getConfig(self) -> list[dict]:
        return loads(fread(self.configFileName, encoding = 'utf-8'))
    
    def writeConfig(self, config: list[dict]):
        fwrite(self.configFileName, dumps(config))
    
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
