# -*- coding: utf-8 -*-
from PySide6           import QtWidgets
from os                import makedirs
from packaging         import version as versioning
from time              import time

from database.elephant import LeafyyPostgresDatabase
from inspection        import LeafyyLogging
from inspection.logger import LeafyyLogger
from inspection.errors import LeafyyErrors
from options           import LeafyyProperties
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
        self.setApplicationVersion(version)

        self.setApplicationName('Leafyy')
        self.setApplicationDisplayName('Листочек')

        print(f'Starting Leafyy v.{self.version}, uncopyrighted')
        print(f'Запуск "Листочка" версии {self.version}, авторские права не защищены')

        self.properties = LeafyyProperties()
        self.postgres = LeafyyPostgresDatabase()

        self.log = LeafyyLogging()
        self.errors = LeafyyErrors()
        self.logger = LeafyyLogger('App')
        self.logger.info(f'Запуск "Листочка" версии {self.version}, авторские права не защищены')
        self.logger.info(f'Инициализация службы...')
        self.logger.info(
            'Инициализирована подсистема журналирования '
            f'(установлен уровень {self.log.globalLevel.name})')
        self.log.setGlobalLogLevel(self.properties('logLevel', 'DEBUG'))

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
            'logs'
        ]

        for dir in DIRS:
            makedirs(dir, exist_ok = True)

    def quit_(self):
        self.web.stop()
        self.exit()
