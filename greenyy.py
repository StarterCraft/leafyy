from PyQt5 import QtCore, QtGui, QtWidgets
from sys import argv, exit

from ui import GreenyyUiManager
from ui.widget.plantWidget import PlantWidget

from device import GreenyyDeviceManager


def main():
    app = QtWidgets.QApplication(argv)
    ui = GreenyyUiManager()
    device = GreenyyDeviceManager()

    ui.generalWindow.mdi.addSubWindow(PlantWidget())
    
    ui.deviceIntegration(device)
    ui.generalWindow.show()

    exit(app.exec_())


if (__name__ == '__main__'):
    main()
