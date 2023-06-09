from PySide6  import QtCore, QtWidgets
from sys    import argv, exit
from webbrowser import open as url


from logger        import GreenyyLogging
from logger.logger import GreenyyLogger
from options       import GreenyyOptions
from ui            import GreenyyUi
from device        import GreenyyHardware
from web           import GreenyyWebServer
from web.api       import GreenyyWebApi


class Greenyy(QtWidgets.QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.log = GreenyyLogging()
        self.logger = GreenyyLogger('App')

        self.options = GreenyyOptions()
        self.log.setGlobalLogLevel(self.options.logLevel)

        self.ui = GreenyyUi()
        self.ui.setupUi()
        self.logger.info('Инициализирован интерфейс')

        self.web = GreenyyWebServer()
        self.logger.info('Инициализировано ядро веб-сервера')

        self.api = GreenyyWebApi()
        self.api.assign(self.web)
        self.web.start()

        self.hardware = GreenyyHardware()
        self.logger.info('Инициализированы устройства')

        self.ui.deviceIntegration()
        self.logger.info('Интеграция устройств в интерфейс проведена')

    def show(self):
        self.ui.show()

        if (not self.ui.isVisible()):
            self.logger.critical(f'Ни одно окно программы не было открыто!')


def main():
    app = Greenyy(argv)
    #app.show()
    url('http://127.0.0.1:8000')

    exit(app.exec())


if (__name__ == '__main__'):
    main()
