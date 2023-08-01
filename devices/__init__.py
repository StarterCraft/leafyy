# -*- coding: utf-8 -*-
from PySide6        import QtSerialPort
from json           import loads, dumps
from typing         import Iterator, List
from autils         import fread, fwrite

from leafyy.generic import LeafyyIterableComponent
from leafyy         import web, postgres

from .generic       import LeafyyStatus, LeafyyByteOperations
from .device        import LeafyyDevice
from .api           import LeafyyDevicesApi
from .models        import Device, Devices, DeviceCounter


class LeafyyDevices(
    LeafyyIterableComponent,
    LeafyyDevicesApi
    ):
    devices: dict[str, LeafyyDevice] = {}

    def __init__(self):
        super().__init__('devices')

        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        self.logger.debug('Информация о портах получена')

        self.config = self.getConfig()

        self.logger.info('Загружены настройки устройств')

    def __getitem__(self, key: int | str) -> LeafyyDevice:
        if (isinstance(key, str)):
            return self.devices[key]

        else:
            return self.devices.values()[key]

    def __iter__(self) -> Iterator[LeafyyDevice]:
        return iter(self.devices.values())

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

    def getConfig(self) -> list[Device]:
        return [Device(**dd._asdict()) for dd in postgres().fetchall('devices.selectDevices')]

    def writeConfig(self, config: list[Device]):
        postgres('devices.truncateDevices')
        postgres().insert('devices.insertDevices', *config)

    def append(self, device: LeafyyDevice):
        self.devices.update({device.address: device})

        self.logger.debug(
            f'Устройство по адресу {device.address} зарегистрировано'
        )

    def remove(self, _device: LeafyyDevice | str):
        if (isinstance(_device, LeafyyDevice)):
            self.devices.remove(_device)

        if (isinstance(_device, str)):
            self.devices.remove(self[_device.name])

        self.logger.debug(
            f'Устройство {_device.name} недоступен'
        )

    def initDevices(self):
        for deviceData in self.config:
            LeafyyDevice(**deviceData.dict())

    def start(self):
        for device in self:
            if (device.isEnabled):
                self.logger.debug('Пытаюсь запустить устройство в системе')
                device.start()
