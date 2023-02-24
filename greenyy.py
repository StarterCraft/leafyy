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
    device.devices[0].port.readyRead.connect(lambda: ui.logWindow.ui.txtLogDisplay.append(str(device.devices[0].port.readLine())))
    ui.logWindow.ui.btnSend.clicked.connect( lambda: device.devices[0].port.write(bytearray(ui.logWindow.ui.lneMessage.text(), 'UTF-8')) )

    ui.deviceIntegration(device)
    ui.generalWindow.show()

    exit(app.exec_())


if (__name__ == '__main__'):
    main()
