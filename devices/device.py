#coding=utf-8
from PySide6         import QtSerialPort
from collections     import deque
from typing          import Any, Iterator

from leafyy.generic  import LeafyyComponent
from leafyy          import options, devices
from devices        import LeafyyStatus
from .message        import LeafyyDeviceMessage
from .models         import Device


class LeafyyDevice(LeafyyComponent):
    def __init__(self, **kwargs):
        super().__init__(
            f'Device-{kwargs.get("address")}',
            displayName = kwargs.get('displayName', 'Устройство без названия')
        )

        if (not kwargs.get('address', None)):
            raise AttributeError('Устройство не может не иметь адреса')
        
        self.description = kwargs.get('description', '')
        self.isEnabled = kwargs.get('enabled', False)
        self.address = kwargs.get('address')
        self.plantsDef = kwargs.get('plants', [])

        self.decodeMode = kwargs.get('decodeMode', 'ascii')
        self.visibleInConsole = kwargs.get('visibleInConsole', True)

        self.status = LeafyyStatus.Disabled
        self.logger.info(f'Инициализация устройства по адресу {self.address}')

        self.port = QtSerialPort.QSerialPort(self.address)
        self.port.setBaudRate(9600)
        self.logger.debug(f'Инициализирован порт {self.address}, 9600 бод')

        self.messages = deque(maxlen = 64)

        devices().add(self)

    def __getitem__(self, _id: int | str) -> NotImplemented:
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
    
    def model(self) -> Device:
        return {
            'address': self.address,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'decodeMode': self.decodeMode
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
        openingResult = self.port.open(QtSerialPort.QSerialPort.ReadWrite)

        if (openingResult): 
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
        if (self.port.canReadLine()):
            msg = LeafyyDeviceMessage(self.address, self.port.read(128))
            self.logger.info(repr(msg))
            self.messages.append(msg)
