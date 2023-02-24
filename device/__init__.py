# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtSerialPort
from json import load, dump
import sys
import traceback


class Device():
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


class DeviceInitializer(QtCore.QRunnable):
    begun = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal()
    initialized = QtCore.pyqtSignal(Device)
    completed = QtCore.pyqtSignal()

    def __init__(self, data: dict) -> None:
        super().__init__()
        self.running = False
        self.data = data

    def run(self):
        #STACKOVERFLOW: https://ru.stackoverflow.com/a/840447/397716
        # Получите args/kwargs здесь; и обработка с их использованием
        try:                       # выполняем метод `execute_this_fn` переданный из Main
            result = Device(**self.data) 
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.initialized.emit(result)
        finally:
            self.completed.emit()            # Done / Готово



class GreenyyDeviceManager:
    def __init__(self):
        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        print('ports:', [(port.portName(), port.description()) for port in self.ports])
        configFile = open('device.json', encoding='utf-8')
        self.config = load(configFile)
        configFile.close()
        self.devices = []
        self.startDevices()
        #for deviceData in self.config:
         #   self.devices.append(Device(**deviceData))
        
    def startDevices(self):
        self.threadpool = QtCore.QThreadPool()
        self.initializers = []

        for deviceData in self.config:
            initializer = DeviceInitializer(deviceData)
            initializer.initialized.connect(lambda: print('YAY'))
            self.initializers.append(initializer)
            self.threadpool.start(initializer)


    def registerDevice(self, it: Device):
        print(62)
        self.devices.append(it)
        print(len(self.devices))
