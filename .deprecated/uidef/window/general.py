# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'g:\Work\Code\leafyy\uisrc\window\general.ui'
#
# Created by: PySide6 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_GeneralWindow(object):
    def setupUi(self, GeneralWindow):
        GeneralWindow.setObjectName("GeneralWindow")
        GeneralWindow.resize(600, 600)
        GeneralWindow.setMinimumSize(QtCore.QSize(600, 600))
        self.mdi = QtWidgets.QMdiArea(GeneralWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mdi.sizePolicy().hasHeightForWidth())
        self.mdi.setSizePolicy(sizePolicy)
        self.mdi.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi.setActivationOrder(QtWidgets.QMdiArea.ActivationHistoryOrder)
        self.mdi.setViewMode(QtWidgets.QMdiArea.SubWindowView)
        self.mdi.setObjectName("mdi")
        self.menubar = QtWidgets.QMenuBar(GeneralWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 26))
        self.menubar.setObjectName("menubar")
        self.meiWindow = QtWidgets.QMenu(self.menubar)
        self.meiWindow.setObjectName("meiWindow")
        self.meiSettings = QtWidgets.QMenu(self.meiWindow)
        self.meiSettings.setObjectName("meiSettings")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        GeneralWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(GeneralWindow)
        self.statusbar.setObjectName("statusbar")
        GeneralWindow.setStatusBar(self.statusbar)
        self.meiDevices = QtGui.QAction(GeneralWindow)
        self.meiDevices.setObjectName("meiDevices")
        self.meiRules = QtGui.QAction(GeneralWindow)
        self.meiRules.setObjectName("meiRules")
        self.meiKeys = QtGui.QAction(GeneralWindow)
        self.meiKeys.setObjectName("meiKeys")
        self.meiLog = QtGui.QAction(GeneralWindow)
        self.meiLog.setCheckable(True)
        self.meiLog.setObjectName("meiLog")
        self.meiGeneral = QtGui.QAction(GeneralWindow)
        self.meiGeneral.setCheckable(True)
        self.meiGeneral.setObjectName("meiGeneral")
        self.meiViewSettings = QtGui.QAction(GeneralWindow)
        self.meiViewSettings.setObjectName("meiViewSettings")
        self.meiSettings.addAction(self.meiDevices)
        self.meiSettings.addAction(self.meiRules)
        self.meiSettings.addAction(self.meiKeys)
        self.meiSettings.addAction(self.meiViewSettings)
        self.meiWindow.addAction(self.meiGeneral)
        self.meiWindow.addAction(self.meiLog)
        self.meiWindow.addAction(self.meiSettings.menuAction())
        self.meiWindow.addSeparator()
        self.menubar.addAction(self.meiWindow.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(GeneralWindow)
        QtCore.QMetaObject.connectSlotsByName(GeneralWindow)

    def retranslateUi(self, GeneralWindow):
        _translate = QtCore.QCoreApplication.translate
        GeneralWindow.setWindowTitle(_translate("GeneralWindow", "Листочек"))
        self.meiWindow.setTitle(_translate("GeneralWindow", "Окно"))
        self.meiSettings.setTitle(_translate("GeneralWindow", "Настройки"))
        self.menuView.setTitle(_translate("GeneralWindow", "Вид"))
        self.meiDevices.setText(_translate("GeneralWindow", "Устройства..."))
        self.meiRules.setText(_translate("GeneralWindow", "Правила..."))
        self.meiKeys.setText(_translate("GeneralWindow", "Клавиши..."))
        self.meiLog.setText(_translate("GeneralWindow", "Журнал"))
        self.meiGeneral.setText(_translate("GeneralWindow", "Основное окно"))
        self.meiViewSettings.setText(_translate("GeneralWindow", "Внешний вид..."))
