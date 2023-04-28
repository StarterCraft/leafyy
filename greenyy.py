from PyQt5 import QtCore, QtWidgets
from sys import argv, exit

from app import GreenyyComponent
from logger import GreenyyLoggingManager
from options import GreenyyOptions
from ui import GreenyyUiManager
from logger.logger import GreenyyLogger
from device import GreenyyHardwareManager


class Greenyy(QtWidgets.QApplication):
    def __init__(self, argv) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.log = GreenyyLoggingManager()
        self.logger = GreenyyLogger('App')

        self.options = GreenyyOptions()
        self.log.setGlobalLogLevel(self.options.logLevel)

        self.ui = GreenyyUiManager()
        self.logger.info('Инициализация интерфейса завершена')

        self.hardware = GreenyyHardwareManager()
        self.logger.info('Инициализация менеджера устройств завершена')

        self.ui.deviceIntegration()
        self.logger.info('Интеграция устройств в интерфейс проведена')

    def show(self):
        for component in self.ui:
            if (component.name in self.options.launchWith):
                component.show()

        if (not self.ui.isVisible()):
            self.logger.critical(f'Ни одно окно программы не было открыто!')


def main():
    from stdlib import printl
    printl(Greenyy.__mro__)
    app = Greenyy(argv)
    app.show()

    exit(app.exec_())


if (__name__ == '__main__'):
    main()
