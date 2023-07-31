# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request

from leafyy  import web

from .models import Devices


class LeafyyDevicesApi:
    api = APIRouter(
        prefix = '/devices',
        tags = ['devices']
    )

    def assignApi(self):
        @self.api.get('', response_model = Devices,
            name = 'Получить информацию о устройствах',
            description = 'Получает информацию о устройствах.')
        async def getDevices(request: Request) -> Devices:
            return self.model()

        web().include_router(self.api)
