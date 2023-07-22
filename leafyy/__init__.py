# -*- coding: utf-8 -*-
from PySide6         import QtCore
from fastapi         import FastAPI
from typing          import Any

import packaging.version as versioning


#Утилитарные функции
def deepget(self: dict, key: str, default: Any = None, sep: str = '.'):
    steps = key.split(sep)
    fetched = self

    for stepKey in steps:
        fetched = fetched.get(stepKey, NotImplemented)

        if (fetched is NotImplemented):
            return default
    
    return fetched

def deepupdate(self: dict, key: str, value: Any, sep: str = '.'):
    steps = key.split(sep)
    container = self

    for stepKey in steps[:-1]:
        container = container.get(stepKey)

    container.update({steps[-1]: value})


#Доступ к компонентам
def app() -> QtCore.QCoreApplication:
    return QtCore.QCoreApplication.instance()

def version() -> versioning.Version:
    return app().version

def tr(*args, **kwargs) -> str:
    return app().translate(*args, **kwargs)

def log():
    return app().log

def errors():
    return app().errors

def options(key: str = None, default: Any = None, sep: str = '.') -> dict | Any:
    if (key):
        return app().options(key, default, sep)
    
    return app().options

def web() -> FastAPI:
    return app().web

def devices():
    return app().devices

def rules():
    return app().rules

def ui():
    return app().ui

def cli(cmd = None):
    if (cmd):
        return app().cli(cmd)
    
    return app().cli
