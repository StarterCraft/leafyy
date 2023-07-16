# -*- coding: utf-8 -*-
from PySide6 import QtCore, QtSerialPort
from json import loads, dumps
from fastapi import FastAPI
from typing import Iterator, List
from autils import fread, fwrite

from leafyy.generic import LeafyyIterableComponent
from leafyy         import web

from .generic import LeafyyStatus, LeafyyByteOperations
from .device  import LeafyyDevice
from .api     import LeafyyDevicesApi
from .models  import Devices


class LeafyyDevices(
    LeafyyIterableComponent,
    LeafyyDevicesApi
    ):
    configFileName = 'device.json'
    devices: List[LeafyyDevice] = []

    def __init__(self):
        super().__init__('devices')

        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        self.logger.debug('Информация о портах получена')

        self.config = self.getConfig()

        self.logger.info('Загружены настройки устройств')

    def __getitem__(self, key: int | str) -> LeafyyDevice:
        if (isinstance(key, str)):
            try:
                return [d for d in self.devices if (d.address == key)][0]
            except IndexError as e:
                raise KeyError(f'Устройства с таким адресом не найдено', key) from e
            
        else:
            return self.devices[key]
        
    def __iter__(self) -> Iterator[LeafyyDevice]:
        return iter(self.devices)
    
    def __len__(self) -> int:
        return len(self.devices)
    
    def model(self) -> Devices:
        return {
            'count': {
                'total': len(self),
                'active': len([1 for d in self if d.status == LeafyyStatus.Active]),
                'disabled': len([1 for d in self if d.status == LeafyyStatus.Disabled]),
                'failed': len([1 for d in self if d.status == LeafyyStatus.Failed])
            },
            'devices': [d.model() for d in self]
        }
    
    def assignApi(self):
        super().assignApi()
        web().mount('/devices', self.api)

    def getConfig(self) -> list[dict]:
        return loads(fread(self.configFileName, encoding = 'utf-8'))
    
    def writeConfig(self, config: list[dict]):
        fwrite(self.configFileName, dumps(config))
    
    def append(self, device: LeafyyDevice):
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
