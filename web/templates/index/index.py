# -*- coding: utf-8 -*-
from leafyy import devices, errors


CONTEXT = {
    'devices': devices().model(),
    'errors': errors().format()
}
