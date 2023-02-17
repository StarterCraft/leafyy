from PyQt5 import QtCore, QtGui, QtWidgets
from sys import argv, exit

from ui import *
from ui.window.general import GeneralWindow
from ui.window.settings import SettingsWindow
from ui.window.log import LogWindow
from ui.widget.plantWidget import PlantWidget


def main():
    app = QtWidgets.QApplication(argv)

    generalWindow = GeneralWindow()
    settingsWindow = SettingsWindow()
    logWindow = LogWindow()

    generalWindow.ui.mdi.addSubWindow(PlantWidget())
    generalWindow.ui.mdi.addSubWindow(PlantWidget())
    generalWindow.ui.mdi.addSubWindow(PlantWidget())
    generalWindow.ui.mdi.addSubWindow(PlantWidget())
    generalWindow.ui.mdi.cascadeSubWindows()

    generalWindow.ui.meiDevices.triggered.connect(settingsWindow.show)
    generalWindow.ui.meiPlants.triggered.connect(settingsWindow.show)


    generalWindow.show()

    exit(app.exec_())


if (__name__ == '__main__'):
    main()
