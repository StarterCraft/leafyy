from PyQt5  import QtCore, QtWidgets
from sys    import argv, exit
from typing import List

from logger        import GreenyyLogging
from logger.logger import GreenyyLogger
from options       import GreenyyOptions
from ui            import GreenyyUi
from device        import GreenyyHardware


class Greenyy(QtWidgets.QApplication):
    def __init__(self, argv) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.log = GreenyyLogging()
        self.logger = GreenyyLogger('App')

        self.options = GreenyyOptions()
        self.log.setGlobalLogLevel(self.options.logLevel)

        self.ui = GreenyyUi()
        self.ui.setupUi()
        self.logger.info('Инициализация интерфейса завершена')

        self.hardware = GreenyyHardware()
        self.hardware.startDevicesSingleThread()
        self.logger.info('Инициализация устройств завершена')

        self.ui.deviceIntegration()
        self.logger.info('Интеграция устройств в интерфейс проведена')

    def show(self):
        self.ui.show()

        if (not self.ui.isVisible()):
            self.logger.critical(f'Ни одно окно программы не было открыто!')


def main():
    app = Greenyy(argv)
    app.show()

    exit(app.exec_())


if (__name__ == '__main__'):
    main()
