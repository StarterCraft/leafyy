# -*- coding: utf-8 -*-
from typing               import Annotated
from glob                 import glob
from os                   import sep
from autils               import fread, fwrite
from requests             import get
from packaging            import version as versioning
from re                   import findall
from datetime             import datetime, timedelta

from fastapi              import APIRouter, Request, Depends
from fastapi.templating   import Jinja2Templates
from starlette.templating import _TemplateResponse
from starlette.exceptions import HTTPException
from fastapi.responses    import Response, HTMLResponse, FileResponse

from fastapi.security     import OAuth2PasswordRequestForm
from hashlib              import pbkdf2_hmac
from jose                 import JWTError
from jose.jwt             import encode as jenc, decode as jdec

from leafyy               import devices as _devices
from leafyy               import log as logging
from leafyy               import errors, postgres
from leafyy               import web, version
from leafyy.generic       import LeafyyComponent
from webutils             import JsResponse, CssResponse, formatExc

from .template            import Template
from .models              import User, AccessibleUser, TokenPair, TokenData
from .exceptions          import *


ALGORITHM = 'HS384'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30
SALT_MULTIPLIER = 381
HMAC_ITERATIONS = 880738


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
        async def getGlobalCss() -> str:
            return fread('web/leafyy.css')

        @self.api.get('/{cssId}.css', response_class = CssResponse, tags = ['uiUtil'],
            name = 'Получить CSS по ID',
            description = 'Получает указанный CSS-файл на основе предоставленного ID.')
        async def getCss(cssId: str) -> str:
            return fread(f'web/templates/{cssId}/{cssId}.css')

        @self.api.get('/leafyy.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить глобальный JS',
            description = 'Получает глобальный JS-файл, необходимый для работы веб-сервиса.')
        async def getGlobalJs() -> str:
            return fread('web/leafyy.js')

        @self.api.get('/{scriptId}.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить JS по ID',
            description = 'Получает указанный JS-файл на основе предоставленного ID.')
        async def getJs(scriptId: str) -> str:
            return fread(f'web/templates/{scriptId}/{scriptId}.js')

        @self.api.get('/site.webmanifest', response_class = Response, tags = ['uiUtil'],
            name = 'Получить веб манифест',
            description = 'Получает файл веб манифеста.')
        async def getWebManifest() -> str:
            return fread('web/site.webmanifest')

        @self.api.get('/resources/{resourceId}', response_class = FileResponse, tags = ['uiUtil'],
            name = 'Получить ресурс по ID',
            description = 'Получает указанный ресурс на основе предоставленного ID.')
        async def getResource(resourceId: str) -> FileResponse:
            return f'web/resources/{resourceId}'

        async def getWebLibraryVersion(libraryId: str) -> versioning.Version:
            '''
            Метод получает версию библиотеки из API и парсит её с помощью модуля versioning.
            '''
            fetched = get(f'https://api.cdnjs.com/libraries/{libraryId}?fields=version').json()
            _version = fetched['version']
            return versioning.parse(_version)

        async def getCachedLibraryVersion(libraryId: str) -> versioning.Version:
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
        async def getWebLibrary(libraryId: str, request: Request) -> str:
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
        async def getCachedLibrary(libraryId: str, request: Request) -> str:
            code = fread(f'web/libraries/{libraryId}.js')
            version = getCachedLibraryVersion(libraryId)

            self.logger.debug(
                f'Загружена локальная библиотека {libraryId} (версия {version})'
                f' для клиента {request.client.host}:{request.client.port}'
            )

            return code

        @self.api.get('/libraries/{libraryId}.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить JS-библиотеку')
        async def getLibrary(libraryId: str, request: Request) -> str:
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
        async def getFavicon() -> FileResponse:
            return f'web/resources/favicon.svg'

        def getSalt() -> str:
            return fread('web/upsalt.token').lower()

        def checkPassword(username: str, plain: str, encoded: str) -> bool:
            try:
                h = pbkdf2_hmac(
                    'sha384',
                    plain.encode('utf-8'),
                    getSalt().encode('utf-8') * SALT_MULTIPLIER,
                    HMAC_ITERATIONS
                    ).hex()
                return h == encoded
            except Exception as e:
                self.logger.error('При входе пользователя, расшифровке пароля произошла следующая ошибка:',
                    exc = e)
                raise UserPasswordException(username) from e

        def selectUser(username: str) -> AccessibleUser:
            thisUser = postgres().fetchone('web.selectUser', username)

            if (not thisUser):
                raise UsernameNotFoundException(username)
            elif (not thisUser.enabled):
                raise UserDisabledException(username)
            else:
                return AccessibleUser(**thisUser._asdict())

        def authenticateUser(username: str, password: str) -> AccessibleUser:
            user = selectUser(username)
            checkPassword(username, password, user.password)
            return user

        async def getUser(token: Annotated[str, Depends(web().authBearer)]) -> AccessibleUser:
            try:
                payload = jdec(token, getSalt(), algorithms = [ALGORITHM])
                username: str = payload['sub']
                tkd = TokenData(username = username)
                return selectUser(tkd.username)
            except UsernameNotFoundException as e:
                self.logger.error('При входе пользователя произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 401,
                    detail = f'Пользователь с именем {username} не существует',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e
            except UserDisabledException as e:
                self.logger.error('При входе пользователя произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 400,
                    detail = 'Невозможно войти с этим именем пользователя',
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

        def createAccessToken(data: dict, expires: timedelta | None = None):
            toEncode = data.copy()
            if expires:
                expire = datetime.utcnow() + expires
            else:
                expire = datetime.utcnow() + timedelta(minute = 5)
            toEncode.update({"exp": expire})
            encodedJwt = jenc(toEncode, getSalt(), algorith = ALGORITHM)
            return encodedJwt

        def createRefreshToken(data: dict, expires: timedelta | None = None):
            toEncode = data.copy()
            if expires:
                expire = datetime.utcnow() + expires
            else:
                expire = datetime.utcnow() + timedelta(day = 0)
            toEncode.update({"exp": expire})
            encodedJwt = jenc(toEncode, getSalt(), algorith = ALGORITHM)
            return encodedJwt

        @self.api.post("/token", response_model = TokenPair)
        async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
            try:
                user = authenticateUser(form_data.username, form_data.password)
                accessTokenExpires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
                accessToken = createAccessToken({"sub": user.username}, accessTokenExpires)
                refreshTokenExpires = timedelta(days = REFRESH_TOKEN_EXPIRE_DAYS)
                refreshToken = createRefreshToken({"sub": user.username}, refreshTokenExpires)
                return {'access_token': accessToken, 'refresh_token': refreshToken, 'token_type': 'bearer'}
            except Exception as e:
                self.logger.error('При входе пользователя произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 401,
                    detail = 'Недопустимые учетные данные',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e
            
        @self.api.post("/token/refresh", response_model = TokenPair)
        async def refreshToken(refresh_token: str):
            try:
                payload = jdec(refresh_token, getSalt(), algorithms = [ALGORITHM])
                username: str = payload['sub']
                tkd = TokenData(username = username)
                selectUser(tkd.username)
                accessTokenExpires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
                accessToken = createAccessToken({"sub": username}, accessTokenExpires)
                refreshTokenExpires = timedelta(days = REFRESH_TOKEN_EXPIRE_DAYS)
                refreshToken = createRefreshToken({"sub": username}, refreshTokenExpires)
                return {'access_token': accessToken, 'refresh_token': refreshToken, 'token_type': 'bearer'}
            except (UsernameNotFoundException, UserDisabledException, JWTError) as e:
                self.logger.error('При обновлении токена произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 401,
                    detail = 'Недопустимый токен обновления',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e

        @self.api.get('/auth', response_class = HTMLResponse,
            name = 'Авторизация',
            description = 'Отрисовывает страницу авторизации.')
        async def getAuthPage(request: Request) -> _TemplateResponse:
            return self['auth'].render(
                request,
                version = str(version())
                )
        
        @self.api.get('/account/{username}', response_class = HTMLResponse,
            name = 'Авторизация',
            description = 'Отрисовывает страницу авторизации.')
        async def getAccountPage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            return self['account'].render(
                request,
                user = user,
                version = str(version())
                )
        
        @self.api.get('/', response_class = HTMLResponse,
            name = 'Главная страница',
            description = 'Отрисовывает главную страницу с информацией о грядках.')
        async def getIndexPage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            return self['index'].render(
                request,
                version = str(version()),
                user = user,
                devices = _devices().model(),
                errors = errors().format()
            )

        @self.api.get('/devices', response_class = HTMLResponse,
            name = 'Страница оборудования',
            description = 'Отрисовывает страницу оборудования с информацией о нем.')
        async def getDevicesPage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            return self['devices'].render(
                request,
                version = str(version()),
                user = user,
                devices = _devices().model()
            )

        @self.api.get('/rules', response_class = HTMLResponse,
            name = 'Правила',
            description = 'Отрисовывает страницу с правилами.')
        async def getRulesPage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            return self['rules'].render(
                request,
                version = str(version()),
                user = user
                )

        @self.api.get('/log', response_class = HTMLResponse,
            name = 'Журнал и консоль',
            description = 'Отрисовывает страницу доступа к консоли и журналу.')
        async def getConsolePage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            return self['console'].render(
                request,
                version = str(version()),
                user = user,
                devices = _devices().model(),
                console = logging().format(),
                logConfig = logging().model()
            )

        @self.api.get('/log/view', response_class = HTMLResponse,
            name = 'Просмотр файла журнала',
            description = 'Отрисовывает страницу со списком файлов журнала.')
        async def getLogListPage(request: Request, user: Annotated[User, Depends(getUser)], reversed = 0) -> _TemplateResponse:
            return self['logList'].render(
                request,
                version = str(version()),
                user = user,
                logData = logging().getLogFolderSummary(reversed),
                reversed = reversed
            )

        @self.api.get('/log/view/{name}', response_class = HTMLResponse,
            name = 'Просмотр файла журнала',
            description = 'Отрисовывает страницу просмотра указанного файла журнала.')
        async def getLogViewPage(request: Request, user: Annotated[User, Depends(getUser)], name: str) -> _TemplateResponse:
            return self['logView'].render(
                request,
                version = str(version()),
                user = user,
                logFile = logging().getLogFile(name, html = True)
            )

        @self.api.get('/doc', response_class = HTMLResponse,
            name = 'Документация',
            description = 'Отрисовывает страницу с документацией.')
        async def getDocPage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            return self['doc'].render(
                request,
                version = str(version()),
                user = user
                )

        web().include_router(self.api)
