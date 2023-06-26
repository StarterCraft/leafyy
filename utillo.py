#coding=utf-8
from typing import overload
from typing import Iterable, Any, Hashable, SupportsInt
from cmd import Cmd
from itertools import product
from collections import Counter
from random import randint, sample
from time import time_ns as timer
from datetime import timedelta
from string import printable, ascii_uppercase
from os import system

cmd = Cmd()


def cls() -> None:
    system('cls')

@overload
def strl(arg: Iterable) -> str: ...
@overload
def strl(*arg: Any) -> str: ...
def strl(*arg) -> str:
    if (len(arg) == 1):
        return ''.join(arg[0])
    
    return ''.join(arg)

@overload
def uniquel(arg: Iterable) -> bool: ...
@overload
def uniquel(*arg: Hashable) -> bool: ...
def uniquel(*arg) -> bool:
    if (len(arg) == 1):
        return len(arg[0]) == len(set(arg[0]))
    
    return len(arg) == len(set(arg))


def uniques(s: str) -> bool:
    return uniquel(list(s))


def products(s: str) -> product:
    return product(s, repeat = len(s))


def convert(intr: int, base: int) -> str:
    res = []
    run = 0
    while (intr != 0):
        run = intr % base
        res.append(run)
        intr = intr // base

    return strl([dict(enumerate([char for char in printable if char not in ascii_uppercase]))[i] for i in res[::-1]])


def lto(targetType, seq: Iterable) -> Iterable:
    return type(seq)(targetType(i) for i in seq)

@overload
def printl(arg: Iterable): ...
@overload
def printl(*arg: Any): ...
def printl(*arg):
    if (len(arg) == 1):
        cmd.columnize([str(item) for item in arg[0]])

    cmd.columnize([str(item) for item in arg])


@overload
def pdt(arg: Iterable): ...
@overload
def pdt(*arg: Any): ...
def pdt(arg: Iterable) -> SupportsInt:
    if (len(arg) == 1):
        p = 1
        for item in arg[0]:
            p *= item

        return p

    p = 1
    for item in arg:
        p *= item

    return p


def fread(name: str, encoding: str = 'utf-8', **kwargs) -> str | bytes | Any:
    '''
    Чтение данных из файла с заданным именем и параметрами открытия.
    '''
    with open(name, **kwargs) as f:
        return f.read()


def fwrite(name: str, data, encoding: str = 'utf-8', mode = 'w', **kwargs) -> None:
    '''
    Запись данных в файл с заданным именем и параметрами открытия.
    '''
    with open(name, mode, **kwargs) as f:
        f.write(data)
