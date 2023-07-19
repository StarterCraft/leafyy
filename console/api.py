# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, Response

from leafyy  import devices, app
from leafyy.generic import LeafyyThreadedWorker

from .models import Order


class LeafyyConsoleApi:
    api = FastAPI(
        name = 'API Листочка: подсистема моментальных команд'
    )

    def assignApi(self):
        @self.api.post('/',
            name = 'Исполнить команду',
            description = 'Исполняет команду, находящуюся в теле запроса.')
        def postExecCmd(request: Request, response: Response, data: Order):
            cmdName = data.data.split()[0]
            cmdArgs = data.data.split()[1:]

            if (data.target == 'server'):
                try:
                    self[cmdName].call(cmdArgs)
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
