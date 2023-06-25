#coding=utf-8
from PySide6 import QtCore, QtWidgets, QtSerialPort
from collections import deque
from typing import Any, Iterator

from leafyy  import LeafyyComponent
from leafyy  import app, ui, options, hardware
from inspection   import LeafyyLogger
from hardware   import LeafyyStatus
from .message import LeafyyDeviceMessage


class LeafyyDevice(LeafyyComponent):
    def __init__(self, **kwargs):
        super().__init__(
            kwargs['name'],
            loggerName = f'Device-{kwargs["address"]}',
            displayName = (
                kwargs['displayName'] if 
                ('displayName' in kwargs.keys()) else
                'Устройство без названия'
            )
        )
        
        self.desc = kwargs['desc']
        self.isEnabled = kwargs['enabled']
        self.address = kwargs['address']
        self.plantsDef = kwargs['plants']

        self.decodeMode = kwargs['decodeMode']
        self.visibleInConsole = kwargs['visibleInConsole']

        self.status = LeafyyStatus.Disabled
        self.logger.info(f'Инициализация устройства по адресу {self.address}')

        self.port = QtSerialPort.QSerialPort(self.address)
        self.port.setBaudRate(9600)
        self.logger.debug(f'Инициализирован порт {self.address}, 9600 бод')

        self.messages = deque(maxlen = 64)
        
        if (self.isEnabled):
            self.logger.debug('Пытаюсь запустить устройство в системе')
            self.start()

        hardware().add(self)

    def __getitem__(self, _id):
        if (isinstance(_id, int)):
            return self.plants[_id]
        
        if (isinstance(_id, str)):
            try: 
                return [plant for plant in self.plants if (plant.name == _id)][0]
            except IndexError as e:
                raise KeyError(f'Грядка {_id} не существует') from e

    def __iter__(self) -> Iterator[Any]:
        return iter(self.plants)

    def __repr__(self) -> str:
        return f'Arduino at {self.address}, baud {self.port.baudRate()}, {self.port.isOpen()}'
    
    def toDict(self) -> dict[str, Any]:
        return {
            'address': self.address,
            'name': self.name,
            'desc': self.desc,
            'status': self.status.value,
            'decodeMode': self.decodeMode,
            'plants': [] #none
        }

    @property
    def logWindowVisibility(self):
        return self.visibleInConsole
    
    @logWindowVisibility.setter
    def logWindowVisibility(self, value: bool):
        self.visibleInConsole = value
        options().setLogWindowSources(self.name, value, 1)

    @property
    def decodeASCII(self):
        return self.decodeASCIIMode
    
    @decodeASCII.setter
    def decodeASCII(self, value: bool):
        self.decodeASCIIMode = value
        options().setLogDecodeASCII(self.address, value)

    def start(self):
        self.logger.debug(f'Пытаюсь открыть порт {self.address}')
        self.port.readyRead.connect(self.receive)
        self.port.open(QtSerialPort.QSerialPort.ReadWrite)

        if (self.port.isOpen()): 
            self.logger.info(f'Порт {self.address} открыт, 9600 бод')
            self.status = LeafyyStatus.Active

        else:
            self.logger.warning(f'Порт {self.address} открыть не удалось')
            self.status = LeafyyStatus.Failed

    def send(self, data: str | bytearray) -> int:
        if (isinstance(data, str)):
            return self.port.write(bytearray(data, 'ascii'))
        
        return self.port.write(data)

    def receive(self):
        msg = LeafyyDeviceMessage(self.address, self.port.readLine())
        self.messages.append(msg)
