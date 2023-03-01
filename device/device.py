from PyQt5 import QtCore, QtSerialPort
from .message import GreenyyDeviceMessage
from collections import deque


class GreenyyDevice():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.port = QtSerialPort.QSerialPort(self.address)
        self.port.setBaudRate(9600)
        self.messages = deque(maxlen = 64)
        self.start()

    def __repr__(self) -> str:
        return f'Arduino at {self.address}, baud {self.port.baudRate()}, {self.port.isOpen()}'

    def start(self):
        self.port.readyRead.connect(self.rec)
        self.port.open(QtSerialPort.QSerialPort.ReadWrite)

    def rec(self):
        msg = GreenyyDeviceMessage(self.address, self.port.readLine())
        self.messages.append(msg)
        print(len(self.messages), repr(msg))
