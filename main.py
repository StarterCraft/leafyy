# -*- coding: utf-8 -*-
from PySide6           import QtWidgets
from sys               import argv, exit as iexit
from os                import makedirs
from typing            import Iterator
from packaging         import version as versioning


from leafyy.generic    import LeafyyComponent
from inspection        import LeafyyLogging
from inspection.errors import LeafyyErrors
from inspection.logger import LeafyyLogger
from options           import LeafyyOptions
from devices           import LeafyyDevices
from web               import LeafyyWebService
from web.api           import LeafyyWebInterface


__version__ = '0.a3'


#Интерфейс на основе Qt GUI отброшен за ненадобностью,
#связанный с ним код закомментирован или удалён


class Leafyy(QtWidgets.QApplication):
    version = versioning.parse(__version__)

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        print(f'Starting Leafyy v.{self.version}, uncopyrighted')
        print(f'Запуск "Листочка" версии {self.version}, авторские права не защищены')

        self.log = LeafyyLogging()
        self.logger = LeafyyLogger('App')

        self.errors = LeafyyErrors()

        self.options = LeafyyOptions()
        self.log.setGlobalLogLevel(self.options('logLevel'))

        self.web = LeafyyWebService()
        self.logger.info('Инициализировано ядро веб-сервера')

        self.devices = LeafyyDevices()
        self.logger.info('Инициализированы устройства')

        self.ui = LeafyyWebInterface()

        self.web.assignApis()

    @staticmethod
    def checkEnvironment():
        DIRS = [
            'logs/buffer'
        ]

        for dir in DIRS:
            makedirs(dir, exist_ok = True)

    def assignApis(self):
        for component in self:
            if (hasattr(component, 'assignApi')):
                component.assignApi(component)


def main():
    Leafyy.checkEnvironment()
    app = Leafyy(argv)
    
    app.web.start()
    app.logger.debug('Hi Ellie!')
    app.devices.initDevices()

    iexit(app.exec())


if (__name__ == '__main__'):
    main()
