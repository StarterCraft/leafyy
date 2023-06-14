from PySide6  import QtCore, QtWidgets
from sys    import argv, exit
from webbrowser import open as url


from inspection        import LeafyyLogging
from inspection.errors import LeafyyErrors
from inspection.logger import LeafyyLogger
from options           import LeafyyOptions
from hardware          import LeafyyHardware
from web               import LeafyyWebServer
from web.api           import LeafyyWebApi


class Leafyy(QtWidgets.QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.log = LeafyyLogging()
        self.logger = LeafyyLogger('App')

        self.errors = LeafyyErrors()

        self.options = LeafyyOptions()
        self.log.setGlobalLogLevel(self.options.logLevel)

        self.web = LeafyyWebServer()
        self.logger.info('Инициализировано ядро веб-сервера')

        self.api = LeafyyWebApi()
        self.api.assign(self.web)
        self.web.start()

        self.hardware = LeafyyHardware()
        self.hardware.startDevices()
        self.logger.info('Инициализированы устройства')


def main():
    app = Leafyy(argv)
    url('http://127.0.0.1:38001/log/view')

    exit(app.exec())


if (__name__ == '__main__'):
    main()
