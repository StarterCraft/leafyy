from PyQt5 import QtCore, QtGui, QtWidgets
from sys import argv, exit

from ui import GreenyyUiManager
from ui.widget.plantWidget import PlantWidget

from device import GreenyyDeviceManager

import typing


class Greenyy(QtWidgets.QApplication):
    def __init__(self, argv: typing.List[str]) -> None:
        super().__init__(argv)
        assert QtWidgets.QApplication.instance() is self

        self.ui = GreenyyUiManager()
        self.device = GreenyyDeviceManager()

        self.ui.generalWindow.mdi.addSubWindow(PlantWidget())

        self.ui.deviceIntegration(self.device)


def main():
    app = Greenyy(argv)
    app.ui.generalWindow.show()
    exit(app.exec_())


if (__name__ == '__main__'):
    main()
