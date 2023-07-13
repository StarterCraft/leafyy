from fastapi import FastAPI, Request

from .models import Devices

class LeafyyDevicesApi:
    api: FastAPI

    def assign(self):
        @self.api.get('/', response_model = Devices,
            name = 'Получить информацию о устройствах',
            description = 'Получает информацию о устройствах.')
        def getDevices(request: Request) -> Devices:
            return self.model()
