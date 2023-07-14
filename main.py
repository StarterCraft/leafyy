from PySide6           import QtWidgets
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


__version__ = '0.1a3'


#Интерфейс на основе Qt GUI отброшен за ненадобностью,
#связанный с ним код закомментирован или удалён


class Leafyy(QtWidgets.QApplication):
    version = versioning.parse(__version__)
    startup = int(time())

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        print(f'Starting Leafyy v.{self.version}, uncopyrighted')
        print(f'Запуск "Листочка" версии {self.version}, авторские права не защищены')

        self.log = LeafyyLogging()
        self.errors = LeafyyErrors()
        self.logger = LeafyyLogger('App')
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
    app.logger.debug('Привет, ребят!')

    app.devices.initDevices()
    app.devices.start()

    app.cli.start()

    iexit(app.exec())


if (__name__ == '__main__'):
    main()
