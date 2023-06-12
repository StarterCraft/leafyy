from PySide6  import QtCore, QtWidgets
from sys    import argv, exit
from webbrowser import open as url


from inspection        import GreenyyLogging
from inspection.logger import GreenyyLogger
from options           import GreenyyOptions
from ui                import GreenyyUi
from hardware          import GreenyyHardware
from web               import GreenyyWebServer
from web.api           import GreenyyWebApi


class Greenyy(QtWidgets.QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.log = GreenyyLogging()
        self.logger = GreenyyLogger('App')

        self.errors = GreenyyErrorStack()

        self.options = GreenyyOptions()
        self.log.setGlobalLogLevel(self.options.logLevel)

        self.web = GreenyyWebServer()
        self.logger.info('Инициализировано ядро веб-сервера')

        self.api = GreenyyWebApi()
        self.api.assign(self.web)
        self.web.start()

        self.hardware = GreenyyHardware()
        self.hardware.startDevices()
        self.logger.info('Инициализированы устройства')
        self.ui.show()

        if (not self.ui.isVisible()):
            self.logger.critical(f'Ни одно окно программы не было открыто!')


def main():
    app = Greenyy(argv)
    url('http://127.0.0.1:8000/')

    exit(app.exec())


if (__name__ == '__main__'):
    main()
