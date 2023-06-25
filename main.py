from PySide6           import QtCore, QtWidgets
from sys               import argv, exit
from os                import makedirs
from webbrowser        import open as url
from enum              import Enum
from packaging         import version as versioning


from inspection        import LeafyyLogging
from inspection.errors import LeafyyErrors
from inspection.logger import LeafyyLogger
from options           import LeafyyOptions
from hardware          import LeafyyHardware
from web               import LeafyyWebServer
from web.api           import LeafyyWebInterfaceApi


__version__ = '0.a3'


#Интерфейс на основе Qt GUI отброшен за ненадобностью,
#связанный с ним код закомментирован или удалён


class LeafyyServiceMode(Enum):
    WebOnly = 0
    QtGuiOnly = 1
    Combined = 2


class Leafyy(QtWidgets.QApplication):
    version = versioning.parse(__version__)

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.log = LeafyyLogging()
        self.logger = LeafyyLogger('App')

        self.errors = LeafyyErrors()

        self.options = LeafyyOptions()
        self.log.setGlobalLogLevel(self.options.get('logLevel'))

        self.web = LeafyyWebServer()
        self.logger.info('Инициализировано ядро веб-сервера')

        self.api = LeafyyWebInterfaceApi()
        self.api.assign(self.web)

        self.hardware = LeafyyHardware()
        self.hardware.startDevices()
        self.logger.info('Инициализированы устройства')

    @staticmethod
    def checkEnvironment():
        DIRS = [
            'logs/buffer'
        ]

        for dir in DIRS:
            makedirs(dir, exist_ok = True)


def main():
    Leafyy.checkEnvironment()

    app = Leafyy(argv)
    
    app.web.startSeparately()

    app.logger.debug('Hi Ellie!')

    exit(app.exec())


if (__name__ == '__main__'):
    main()
