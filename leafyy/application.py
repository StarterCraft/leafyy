# -*- coding: utf-8 -*-
from PySide6           import QtCore, QtWidgets
from sys               import argv, exit as iexit
from os                import makedirs
from packaging         import version as versioning
from time              import time

from inspection        import LeafyyLogging
from inspection.logger import LeafyyLogger
from inspection.errors import LeafyyErrors
from options           import LeafyyOptions
from console           import LeafyyConsole
from devices           import LeafyyDevices
from web               import LeafyyWebService
from web.api           import LeafyyWebInterface


class Leafyy(QtWidgets.QApplication):
    startup = int(time())

    def __init__(self, argv: list[str], version: str) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.version = versioning.parse(version)

        print(f'Starting Leafyy v.{self.version}, uncopyrighted')
        print(f'Запуск "Листочка" версии {self.version}, авторские права не защищены')

        self.log = LeafyyLogging()
        self.errors = LeafyyErrors()
        self.logger = LeafyyLogger('App')
        self.logger.info(f'Запуск "Листочка" версии {self.version}, авторские права не защищены')
        self.logger.info(f'Инициализация службы...')
        self.logger.info(
            'Инициализирована подсистема журналирования '
            f'(установлен уровень {self.log.globalLevel.name})')

        self.options = LeafyyOptions()
        self.log.setGlobalLogLevel(self.options('logLevel'))

        self.cli = LeafyyConsole()
        self.logger.info('Инициализирована подсистема консоли')

        self.web = LeafyyWebService()
        self.logger.info('Инициализирована подсистема веб-сервера')

        self.devices = LeafyyDevices()
        self.logger.info('Инициализирована подсистема устройств')

        self.ui = LeafyyWebInterface()
        self.logger.info('Инициализирован веб-интерфейс')

    def start(self):
        self.devices.initDevices()
        self.devices.start()
        
        self.web.start()
        self.logger.debug('Привет, ребят!')

        self.web.assignApis()
        self.cli.assignClis()

    @staticmethod
    def checkEnvironment():
        DIRS = [
            'logs/buffer'
        ]

        for dir in DIRS:
            makedirs(dir, exist_ok = True)

    def quit_(self):
        self.web.stop()
        self.exit()