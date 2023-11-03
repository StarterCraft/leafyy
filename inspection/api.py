# -*- coding: utf-8 -*-
from typing   import Annotated

from fastapi  import APIRouter, Request, Response, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse

from jose.exceptions import JWTError

from autils   import fread

from leafyy   import web, ui

from .models  import *
from web.models     import User, AccessibleUser
from web.exceptions import *



class LeafyyLoggingApi:
    api = APIRouter(
        prefix = '/log',
        tags = ['log']
    )

    def assignApi(self):
        async def getUser(token: Annotated[str, Depends(web().authBearer)]) -> AccessibleUser:
            try:
                return ui().auth.resolveUser(token)
            except UsernameNotFoundException as e:
                self.logger.error(f'При входе пользователя {e.username} произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 401,
                    detail = f'Пользователь с именем {e.username} не существует',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e
            except UserDisabledException as e:
                self.logger.error(f'При входе пользователя {e.username} произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 400,
                    detail = f'Невозможно войти с именем пользователя {e.username},'
                             'учётная запись недоступна',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e
            except (UserPasswordException, KeyError, JWTError) as e:
                self.logger.error('При входе пользователя произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 401,
                    detail = 'Недопустимые учетные данные',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e

        @self.api.post('',
            name = 'Опубликовать сообщение журнала сервера',
            description = 'Приказывает серверу опубликовать сообщение журнала от логгера Web.')
        async def postLogReport(request: Request, user: Annotated[User, Depends(getUser)], response: Response, message: LogRecord):
            self[message.logger].publish(message.level, message.message.replace(
                'USER_IP', f'{request.client.host}:{request.client.port}'
            ))

            response.status_code = 202
            return response

        @self.api.get('/update', response_model = list[str],
            name = 'Получить стек новых сообщений консоли, начиная с времени stamp')
        async def getLogUpdate(request: Request, user: Annotated[User, Depends(getUser)], begin: PositiveFloat):
            return self.format(begin = begin)

        @self.api.get('/{name}', response_class = PlainTextResponse,
            name = 'Скачивание файла журнала',
            description = 'Отправляет указанный файл журнала.')
        async def getLogFile(request: Request, user: Annotated[User, Depends(getUser)], name: str) -> PlainTextResponse:
            return fread(f'logs/{name}')

        @self.api.get('/config', response_model = LogConfig,
            name = 'Получить настройки журналирования',
            description = '')
        async def getLogConfig(request: Request, user: Annotated[User, Depends(getUser)]):
            c = {
                'level': self.globalLevel.name,
                'sources': self.getLogSources()
                }

            return c

        @self.api.put('/config',
            name = 'Записать настройки журналирования',
            description = '')
        async def putLogConfig(config: LogConfig, request: Request, user: Annotated[User, Depends(getUser)]):
            self.setGlobalLogLevel(config.level)
            self.configLogSources(config.sources)

        web().include_router(self.api)
