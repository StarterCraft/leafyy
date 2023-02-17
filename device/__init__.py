from PyQt5 import QtCore, QtSerialPort
from json import load, dump


class Device():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.port = QtSerialPort.QSerialPort(kwargs['address'])
        self.port.setOpenMode(QtSerialPort.QSerialPort.OpenModeFlag.ReadWrite)
        self.port.open(QtSerialPort.QSerialPort.OpenModeFlag.ReadWrite)
        print(self)


    def __repr__(self) -> str:
        return f'Arduino at {self.address}, baud {self.port.baudRate()}, {self.port.isOpen()}'


class DeviceInitializer(QtCore.QObject, QtCore.QRunnable):
    completed = QtCore.pyqtSignal(Device)

    def __init__(self, data: dict) -> None:
        super().__init__()
        self.running = False
        self.data = data

    def run(self):
        print('BEGIN')
        d = Device(**self.data)
        print('EMIT')
        self.completed.emit(d)



class GreenyyDeviceManager:
    def __init__(self):
        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        print('ports:', [(port.portName(), port.description()) for port in self.ports])
        configFile = open('device.json', encoding='utf-8')
        self.config = load(configFile)
        self.devices = []
        configFile.close()
        self.startDevices()
        #for deviceData in self.config:
         #   self.devices.append(Device(**deviceData))
        
    def startDevices(self):
        self.threadpool = QtCore.QThreadPool()

        for deviceData in self.config:
            initializer = DeviceInitializer(deviceData)
            initializer.completed.connect(self.registerDevice)
            self.threadpool.start(initializer.run)

    def registerDevice(self, it: Device):
        self.devices.append(it)
        print(Device)
