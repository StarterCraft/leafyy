from PyQt5 import QtCore, QtWidgets
from sys import argv, exit

from logger import GreenyyLoggingManager
from options import GreenyyUserOptions
from ui import GreenyyUiManager
from logger.logger import GreenyyLogger
from device import GreenyyDeviceManager


class Greenyy(QtWidgets.QApplication):
    def __init__(self, argv) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.logging = GreenyyLoggingManager()
        self.logger = GreenyyLogger('Root')

        self.userOptions = GreenyyUserOptions()
        self.logging.setGlobalLogLevel(self.userOptions.logLevel)

        self.ui = GreenyyUiManager()
        self.logger.info('Инициализация интерфейса завершена')

        self.device = GreenyyDeviceManager()
        self.logger.info('Инициализация менеджера устройств завершена')

        self.ui.deviceIntegration()
        self.logger.info('Интеграция устройств в интерфейс проведена')
        

def main():
    app = Greenyy(argv)
    app.ui.generalWindow.show()

    exit(app.exec_())


if (__name__ == '__main__'):
    main()
