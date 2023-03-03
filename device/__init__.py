# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtSerialPort, QtWidgets
from .device import GreenyyDevice
from .initializer import GreenyyDeviceInitializer
from logger.logger import GreenyyLogger
from json import load, dump
import sys
import traceback


class GreenyyDeviceManager(QtCore.QObject):
    def __init__(self, w: QtWidgets.QTextEdit):
        super().__init__()
        self.logger = GreenyyLogger('DeviceManager', w)

        self.ports = QtSerialPort.QSerialPortInfo().availablePorts()
        self.logger.debug('Информация о портах получена')

        configFile = open('device.json', encoding='utf-8')
        self.config = load(configFile)
        configFile.close()
        self.devices = []

        #self.threads = []
        #self.startDevices()
        #INITIALIZER не работает. Пока без многопотокового решения
        self.startDevicesSingleThread() #временное решение. Или постоянное...

    def startDevicesSingleThread(self):
        for deviceData in self.config:
            self.devices.append(GreenyyDevice(**deviceData))
        
    def startDevices(self):
        for deviceData in self.config:
            self.startDevice(deviceData)

        for th in self.threads:
            th.start()

        #for inj in self.inis:
         #   inj.start()

    def startDevice(self, deviceData):
        ini = GreenyyDeviceInitializer(deviceData)
        ini.initialized.connect(self.print_output)
        self.threads.append(ini)

    def initialization(self, **data):
        return GreenyyDevice(**data)

    @QtCore.pyqtSlot(object)
    def print_output(self, s):
        print("\ndef print_output(self, s):", s)
        self.devices.append(s)
    
    def thread_complete(self):
        print("\nTHREAD ЗАВЕРШЕН!, self->", self)

    def registerDevice(self, it: GreenyyDevice):
        print(62)
        self.devices.append(it)
        print(len(self.devices))
