# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request, Response

from leafyy  import devices, web
from leafyy.generic import LeafyyThreadedWorker

from .models import Order


class LeafyyConsoleApi:
    api = APIRouter(
        prefix = '/console',
    )

    def assignApi(self):
        @self.api.post('', tags = ['console'],
            name = 'Исполнить команду',
            description = 'Исполняет команду, находящуюся в теле запроса.')
        async def postExecCmd(request: Request, response: Response, data: Order):
            cmdName = data.data.split()[0]
            cmdArgs = data.data.split()[1:]

            if (data.target == 'server'):
                try:
                    self(cmdName, cmdArgs)
                    response.status_code = 202
                    return response
                except KeyError:
                    self.logger.error(
                        f'Команда {cmdName} не распознана. Используйте help для перечисления '
                        'всех допустимых команд.')
                    response.status_code = 204
                    return response
            else:
                devices(data.target).send(devices().convertData(data.data, data.type))

        web().include_router(self.api)
