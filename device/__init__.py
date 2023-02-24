# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtSerialPort
from .device import GreenyyDevice
from .initializer import GreenyyDeviceInitializer
from logger import GreenyyLogger
from json import load, dump
import sys
import traceback


class GreenyyDeviceManager:
    def __init__(self):
        #self.logger = GreenyyLogger('DeviceManager')
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

        for deviceData in self.config:
            initializer = GreenyyDeviceInitializer(deviceData)
            initializer.signals.completed.connect(lambda: print('121321323'))
            self.threadpool.start(initializer)

        
    def registerDevice(self, it: GreenyyDevice):
        print(62)
        self.devices.append(it)
        print(len(self.devices))
