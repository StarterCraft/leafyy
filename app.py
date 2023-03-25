from PyQt5 import QtWidgets

def logging():
    return QtWidgets.QApplication.instance().logging

def userOptions():
    return QtWidgets.QApplication.instance().userOptions

def ui():
    return QtWidgets.QApplication.instance().ui

def device():
    return QtWidgets.QApplication.instance().device
