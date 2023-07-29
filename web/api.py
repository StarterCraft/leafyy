# -*- coding: utf-8 -*-
from typing               import Annotated
from glob                 import glob
from os                   import sep
from autils               import fread, fwrite
from requests             import get
from packaging            import version as versioning
from re                   import findall

from fastapi              import APIRouter, Request, Depends
from fastapi.templating   import Jinja2Templates
from starlette.templating import _TemplateResponse
from starlette.exceptions import HTTPException
from fastapi.responses    import Response, HTMLResponse, FileResponse

from leafyy               import devices as _devices
from leafyy               import log as logging
from leafyy               import errors
from leafyy               import web, version
from leafyy.generic       import LeafyyComponent
from webutils             import JsResponse, CssResponse

from .template            import Template


class LeafyyWebInterface(LeafyyComponent):
    api = APIRouter(
        tags = ['ui']
    )

    def __init__(self) -> None:
        super().__init__('WebUi')

        self.jinja = Jinja2Templates('web/templates')

        self.pages = self.loadTemplates()

    def __getitem__(self, key: str) -> Template:
        return self.pages[key]

    def loadTemplates(self) -> dict[str, Template]:
        td = {}        
        templateNames = [name.split(sep)[-1] for name in glob('web/templates/*')]

        for name in templateNames:
            td.update({name: Template(name, self.jinja)})

        return td

    def assignApi(self):
        @self.api.get('/leafyy.css', response_class = CssResponse, tags = ['uiUtil'],
            name = 'Получить глобальный CSS',
            description = 'Получает глобальный CSS-файл, необходимый для работы веб-сервиса.')
        def getGlobalCss() -> str:
            return fread('web/leafyy.css')

        @self.api.get('/{cssId}.css', response_class = CssResponse, tags = ['uiUtil'],
            name = 'Получить CSS по ID',
            description = 'Получает указанный CSS-файл на основе предоставленного ID.')
        def getCss(cssId: str) -> str:
            return fread(f'web/templates/{cssId}/{cssId}.css')

        @self.api.get('/leafyy.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить глобальный JS',
            description = 'Получает глобальный JS-файл, необходимый для работы веб-сервиса.')
        def getGlobalJs() -> str:
            return fread('web/leafyy.js')

        @self.api.get('/{scriptId}.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить JS по ID',
            description = 'Получает указанный JS-файл на основе предоставленного ID.')
        def getJs(scriptId: str) -> str:
            return fread(f'web/templates/{scriptId}/{scriptId}.js')

        @self.api.get('/site.webmanifest', response_class = Response, tags = ['uiUtil'],
            name = 'Получить веб манифест',
            description = 'Получает файл веб манифеста.')
        def getWebManifest() -> str:
            return fread('web/site.webmanifest')

        @self.api.get('/resources/{resourceId}', response_class = FileResponse, tags = ['uiUtil'],
            name = 'Получить ресурс по ID',
            description = 'Получает указанный ресурс на основе предоставленного ID.')
        def getResource(resourceId: str) -> FileResponse:
            return f'web/resources/{resourceId}'

        def getWebLibraryVersion(libraryId: str) -> versioning.Version:
            '''
            Метод получает версию библиотеки из API и парсит её с помощью модуля versioning.
            '''
            fetched = get(f'https://api.cdnjs.com/libraries/{libraryId}?fields=version').json()
            _version = fetched['version']
            return versioning.parse(_version)

        def getCachedLibraryVersion(libraryId: str) -> versioning.Version:
            '''
            Метод получает версию локальной копии библиотеки из файла, парсит её и возвращает.
            '''
            code = fread(f'web/libraries/{libraryId}.js')
            regexMatch = findall(r'(v([0-9A-Za-z][.]{0,1})+)|$', code)[0]
            version = 'undefined'

            if (regexMatch[0]):
                version = regexMatch[0][1:]

            return versioning.parse(version)

        @self.api.get('/libraries/web/{libraryId}.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить актуальную JS-библиотеку')
        def getWebLibrary(libraryId: str, request: Request) -> str:
            '''
            Метод получает новую версию библиотеки из API, сохраняет её в файл и возвращает её в виде строки.
            '''
            fetched = get(f'https://api.cdnjs.com/libraries/{libraryId}?fields=latest,version').json()
            code = get(fetched['latest']).text
            version = fetched['version']

            #Проверка версии локальной библиотеки уже проведена,
            #поэтому здесь она не ведётся
            fwrite(f'web/libraries/{libraryId}.js', code)

            self.logger.info(
                f'Загружена локальная библиотека {libraryId} (версия {version})'
                f' для клиента {request.client.host}:{request.client.port}. Локальная библиотека обновлена'
            )

            return code

        @self.api.get('/libraries/cache/{libraryId}.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить кэшированную JS-библиотеку')
        def getCachedLibrary(libraryId: str, request: Request) -> str:
            code = fread(f'web/libraries/{libraryId}.js')
            version = getCachedLibraryVersion(libraryId)

            self.logger.debug(
                f'Загружена локальная библиотека {libraryId} (версия {version})'
                f' для клиента {request.client.host}:{request.client.port}'
            )

            return code

        @self.api.get('/libraries/{libraryId}.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить JS-библиотеку')
        def getLibrary(libraryId: str, request: Request) -> str:
            '''
            Метод получает библиотеку для клиента из API или из локальной копии
            в зависимости от того, какая версия библиотеки актуальна. Если 
            актуальность не удаётся проверить, метод подключит локальную копию и
            вернёт её.
            '''
            d = ''

            try: 
                #Если на сервере хранится актуальная версия библиотеки,
                #подключить её. Если вышла новая, скачать её и записать
                #в файл.
                if (getCachedLibraryVersion(libraryId) < getWebLibraryVersion(libraryId)):
                    d = getWebLibrary(libraryId, request)

                else:
                    d = getCachedLibrary(libraryId, request)
                
            except Exception as e:
                self.logger.error(
                    f'Не удалось подключить актуальную версию библиотеки {libraryId} '
                    f'для клиента {request.client.host}: {type(e).__name__}: {e}. Подключаю локальную '
                    'библиотеку...'
                ) 
                d = getCachedLibrary(libraryId, request)

            return d

        @self.api.get('/favicon.ico', response_class = FileResponse, tags = ['uiUtil'],
            name = 'Получить favicon',
            description = 'Получает favicon.')
        def getFavicon() -> FileResponse:
            return f'web/resources/favicon.svg'

        @self.api.get('/auth', response_class = HTMLResponse,
            name = 'Авторизация',
            description = 'Отрисовывает страницу авторизации.')
        def getAuthPage(request: Request) -> _TemplateResponse:
            return self['auth'].render(
                request,
                version = str(version())
                )

        @self.api.get('/', response_class = HTMLResponse, 
            name = 'Главная страница',
            description = 'Отрисовывает главную страницу с информацией о грядках.')
        def getIndexPage(request: Request) -> _TemplateResponse:
            return self['index'].render(
                request,
                version = str(version()),
                devices = _devices().model(),
                errors = errors().format()
            )

        @self.api.get('/devices', response_class = HTMLResponse,
            name = 'Страница оборудования',
            description = 'Отрисовывает страницу оборудования с информацией о нем.')
        def getDevicesPage(request: Request) -> _TemplateResponse:
            return self['devices'].render(
                request,
                version = str(version()),
                devices = _devices().model()
            )

        @self.api.get('/rules', response_class = HTMLResponse,
            name = 'Правила',
            description = 'Отрисовывает страницу с правилами.')
        def getRulesPage(request: Request) -> _TemplateResponse:
            return self['rules'].render(
                request,
                version = str(version())
                )

        @self.api.get('/log', response_class = HTMLResponse,
            name = 'Журнал и консоль',
            description = 'Отрисовывает страницу доступа к консоли и журналу.')
        def getConsolePage(request: Request) -> _TemplateResponse:
            return self['console'].render(
                request,
                version = str(version()),
                devices = _devices().model(),
                console = logging().formatRecords(logging().getLogRecords()),
                logConfig = logging().model()
            )

        @self.api.get('/log/view', response_class = HTMLResponse,
            name = 'Просмотр файла журнала',
            description = 'Отрисовывает страницу со списком файлов журнала.')
        def getLogListPage(request: Request, reversed = 0) -> _TemplateResponse:
            return self['logList'].render(
                request,
                version = str(version()),
                logData = logging().getLogFolderSummary(reversed),
                reversed = reversed
            )

        @self.api.get('/log/view/{name}', response_class = HTMLResponse,
            name = 'Просмотр файла журнала',
            description = 'Отрисовывает страницу просмотра указанного файла журнала.')
        def getLogViewPage(request: Request, name: str) -> _TemplateResponse:
            return self['logView'].render(
                request,
                version = str(version()),
                logFile = logging().getLogFile(name, html = True)
            )
        
        @self.api.get('/doc', response_class = HTMLResponse,
            name = 'Документация',
            description = 'Отрисовывает страницу с документацией.')
        def getDocPage(request: Request) -> _TemplateResponse:
            return self['doc'].render(
                request,
                version = str(version())
                )
        
        @web().exception_handler(HTTPException)
        def error(request: Request, exception: HTTPException) -> _TemplateResponse:
            return self['error'].render(
                request, 
                statusCode = exception.status_code,
                exception = exception
                )

        web().include_router(self.api)
