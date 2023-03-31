#coding=utf-8
from PyQt5 import QtCore, QtWidgets, QtSerialPort
from collections import deque

from app import ui, userOptions
from logger import GreenyyLogger
from device import GreenyyStatus
from .message import GreenyyDeviceMessage


class GreenyyDevice():
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.desc = kwargs['desc']
        self.isEnabled = kwargs['enabled']
        self.address = kwargs['address']
        self.tempSensorDef = kwargs['unifiedTempSensor']
        self.plantsDef = kwargs['plants']

        self.logWindowVisibility = userOptions().logWindowSources(self.address, 1)
        self.decodeASCIIMode = userOptions().logDecodeASCII(self.address)

        self.status = GreenyyStatus.Disabled
        self.logger = GreenyyLogger(f'Device[{self.address}]')
        self.logger.info(f'Инициализация устройства по адресу {self.address}')

        self.port = QtSerialPort.QSerialPort(self.address)
        self.port.setBaudRate(9600)
        self.logger.debug(f'Инициализирован порт {self.address}, 9600 бод')

        self.messages = deque(maxlen = 64)

        self.liwDevicesItem = QtWidgets.QTreeWidgetItem(
            ui().settingsWindow.treeDevices, 
            [self.name,
             self.status.name,
             f'Arduino {self.address}'])
        
        if (self.isEnabled):
            self.logger.debug('Пытаюсь запустить устройство в системе')
            self.start()

    def __getitem__(self, _id):
        if (isinstance(_id, int)):
            return self.plants[_id]
        
        if (isinstance(_id, str)):
            try: 
                return [plant for plant in self.plants if (plant.name == _id)][0]
            except IndexError as e:
                raise KeyError(f'Грядка {_id} не существует') from e

    def __repr__(self) -> str:
        return f'Arduino at {self.address}, baud {self.port.baudRate()}, {self.port.isOpen()}'

    @property
    def logWindowVisibility(self):
        return self.logWindow
    
    @logWindowVisibility.setter
    def logWindowVisibility(self, value: bool):
        self.logWindow = value
        userOptions().setLogWindowSources(self.name, value, 1)

    @property
    def decodeASCII(self):
        return self.decodeASCIIMode
    
    @decodeASCII.setter
    def decodeASCII(self, value: bool):
        self.decodeASCIIMode = value
        userOptions().setLogDecodeASCII(self.address, value)

    def start(self):
        self.logger.debug(f'Пытаюсь открыть порт {self.address}')
        self.port.readyRead.connect(self.receive)
        self.port.open(QtSerialPort.QSerialPort.ReadWrite)

        if (self.port.isOpen()): 
            self.logger.info(f'Порт {self.address} открыт, 9600 бод')
            self.status = GreenyyStatus.Enabled
            self.liwDevicesItem.setText(1, self.status.name)

        else:
            self.logger.warning(f'Порт {self.address} открыть не удалось')
            self.status = GreenyyStatus.Failed
            self.liwDevicesItem.setText(1, self.status.name)

    def receive(self):
        msg = GreenyyDeviceMessage(self.address, self.port.readLine())
        self.messages.append(msg)
