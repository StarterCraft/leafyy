from PyQt5 import QtCore, QtSerialPort


class GreenyyDevice():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.port = QtSerialPort.QSerialPort(self.address)
        self.port.setBaudRate(9600)
        print(self.port.open(QtSerialPort.QSerialPort.ReadWrite))
        self.port.readyRead.connect(lambda: print('HELLO'))


    def __repr__(self) -> str:
        return f'Arduino at {self.address}, baud {self.port.baudRate()}, {self.port.isOpen()}'


    def d_printreceifs(self):
        receif = self.port.readLine()
        print(receif)
        
