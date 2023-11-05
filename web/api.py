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

from fastapi.security     import OAuth2PasswordRequestForm
from jose                 import JWTError

from leafyy               import devices as _devices
from leafyy               import log as logging
from leafyy               import errors
from leafyy               import web, version
from leafyy.generic       import LeafyyComponent
from webutils             import JsResponse, CssResponse

from .auth                import LeafyyAuthentificator
from .template            import Template
from .models              import User, AccessibleUser, UserForPasswordChange, TokenString, TokenPair
from .exceptions          import *


JS_LIBRARY_UPDATE_TIMEOUT = 5


class LeafyyWebInterface(LeafyyComponent):
    api = APIRouter(
        tags = ['ui']
    )

    auth = LeafyyAuthentificator()

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

        def getWebLibraryVersion(libraryId: str) -> versioning.Version:
            '''
            Метод получает версию библиотеки из API и парсит её с помощью модуля versioning.
            '''
            version = '0.0.1dev1'

            try:
                fetched = get(f'https://api.cdnjs.com/libraries/{libraryId}?fields=version', timeout = JS_LIBRARY_UPDATE_TIMEOUT).json()
                version = fetched['version']
            except KeyError:
                pass

            return versioning.parse(version)

        def getCachedLibraryVersion(libraryId: str) -> versioning.Version:
            '''
            Метод получает версию локальной копии библиотеки из файла, парсит её и возвращает.
            '''
            code = fread(f'web/libraries/{libraryId}.js')
            regexMatch = findall(r'(v([0-9A-Za-z][.]{0,1})+)|$', code)[0]
            version = '0.0.1dev1'

            if (regexMatch[0]):
                version = regexMatch[0][1:]

            return versioning.parse(version)

        @self.api.get('/libraries/web/{libraryId}.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить актуальную JS-библиотеку')
        def getWebLibrary(libraryId: str, request: Request) -> str:
            '''
            Метод получает новую версию библиотеки из API, сохраняет её в файл и возвращает её в виде строки.
            '''
            fetched = get(f'https://api.cdnjs.com/libraries/{libraryId}?fields=latest,version', timeout = JS_LIBRARY_UPDATE_TIMEOUT).json()
            code = get(fetched['latest']).text
            version = fetched['version']

            #Проверка версии локальной библиотеки уже проведена,
            #поэтому здесь она не ведётся
            fwrite(f'web/libraries/{libraryId}.js', code)

            self.logger.info(
                f'Загружена локальная библиотека {libraryId} (версия {version})'
                f' для клиента {request.client.host}. Локальная библиотека обновлена'
            )

            return code

        @self.api.get('/libraries/cache/{libraryId}.js', response_class = JsResponse, tags = ['uiUtil'],
            name = 'Получить кэшированную JS-библиотеку')
        def getCachedLibrary(libraryId: str, request: Request) -> str:
            code = fread(f'web/libraries/{libraryId}.js')
            version = 'undefined'
            try: version = getCachedLibraryVersion(libraryId)
            except: pass

            self.logger.debug(
                f'Загружена локальная библиотека {libraryId} (версия {version})'
                f' для клиента {request.client.host}'
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
        async def getFavicon() -> FileResponse:
            return f'web/resources/favicon.svg'

        async def getUser(request: Request, token: Annotated[str, Depends(web().authBearer)]) -> AccessibleUser:
            try:
                return self.auth.resolveUser(token)
            except UsernameNotFoundException as e:
                self.logger.error(f'При входе пользователя {e.username} @ {request.client.host} произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 401,
                    detail = f'Пользователь с именем {e.username} не существует',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e
            except UserDisabledException as e:
                self.logger.error(f'При входе пользователя {e.username} @ {request.client.host} произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 400,
                    detail = f'Невозможно войти с именем пользователя {e.username},'
                             'учётная запись недоступна',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e
            except (UserPasswordException, KeyError, JWTError) as e:
                self.logger.error(f'При входе пользователя с {request.client.host} произошла следующая ошибка:',
                    exc = e)
                raise HTTPException(
                    status_code = 401,
                    detail = 'Недопустимые учетные данные',
                    headers = {"WWW-Authenticate": "Bearer"}
                ) from e

        @self.api.post('/account/add')
        def postAddUser(request: Request, user: Annotated[User, Depends(getUser)], data: AccessibleUser):
            try:
                if (not (user.warden or user.master)):
                    raise PermissionError(
                        f'Пользователь {user.username} @ {request.client.host} не имеет прав на эту операцию')

                return self.auth.addUser(data)
            except ValueError as e:
                self.logger.error('При создании нового профиля пользователя произошла следующая ошибка:',
                    exc = e)
                raise e

        @self.api.put('/account/password')
        def putUserPassword(request: Request, user: Annotated[User, Depends(getUser)], data: UserForPasswordChange):
            try:
                if (not (user.warden or user.master)):
                    raise PermissionError(
                        f'Пользователь {user.username} @ {request.client.host} не имеет прав на эту операцию')

                return self.auth.setUserPassword(data)
            except ValueError as e:
                self.logger.error('При изменении пароля пользователя произошла следующая ошибка:',
                    exc = e)
                raise e
            
        @self.api.put('/account/status')
        def putUserStatus(request: Request, user: Annotated[User, Depends(getUser)], data: User):
            try:
                if (not (user.warden or user.master)):
                    raise PermissionError(
                        f'Пользователь {user.username} @ {request.client.host} не имеет прав на эту операцию')
                
                return self.auth.setUserStatus(data)
            except ValueError as e:
                self.logger.error('При изменении статуса пользователя произошла следующая ошибка:',
                    exc = e)
                raise e

        @self.api.post('/token', response_model = TokenPair)
        def accessToken(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
            try:
                print(form_data.username, form_data.password)
                return self.auth.getAccessToken(form_data)
            except Exception as e:
                self.logger.error('При входе пользователя произошла следующая ошибка:',
                    exc = e)
                raise e

        @self.api.post('/token/verify')
        async def verifyToken(token: TokenString):
            try:
                self.logger.info('received ' + token.token)
                self.auth.resolveUser(token.token, verifyOnly = True)
                return {'verified': True}
            except Exception as e:
                self.logger.error('При проверке токена пользователя произошла следующая ошибка:',
                    exc = e)
                return {'verified': False}

        @self.api.post('/token/refresh', response_model = TokenPair)
        async def refreshToken(refresh_token: TokenString):
            try:
                return self.auth.getRefreshToken(refresh_token.token)
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
            description = 'Пытается авторизовать пользователя по токену.')
        async def getAuthentication(request: Request, to: str = '/') -> _TemplateResponse:
            return self['auth'].render(
                request,
                redirectAfter = to,
                version = str(version())
                )

        @self.api.post('/auth/finish', response_class = HTMLResponse,
            name = 'Вход',
            description = 'Позволяет веб-интерфейсу записать токен в куки.')
        async def getLoginResult(request: Request, to: str, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> _TemplateResponse:
            status = ''
            try:
                td = accessToken(form_data)
                return self['authFinish'].render(
                    request,
                    accessToken = td['access_token'],
                    refreshToken = td['refresh_token'],
                    redirectAfter = to
                )

            except UsernameNotFoundException as e:
                status = f'<span class="negative">Учётной записи пользователя <b>{e.username}</b> не нашлось.</span>'

                return self['authLogin'].render(
                    request,
                    statusMessage = status,
                    redirectAfter = to,
                    version = str(version())
                    )

            except UserDisabledException as e:
                status = f'<span class="negative">Учётная запись пользователя <b>{e.username}</b> отключена.</span>'

                return self['authLogin'].render(
                    request,
                    statusMessage = status,
                    redirectAfter = to,
                    version = str(version())
                    )

            except (UserPasswordException, KeyError, JWTError) as e:
                status = f'<span class="negative">Неверные данные учётной записи: имя пользователя или пароль.</span>'

                return self['authLogin'].render(
                    request,
                    statusMessage = status,
                    redirectAfter = to,
                    version = str(version())
                    )

        @self.api.get('/auth/logout', response_class = HTMLResponse,
            name = 'Выход',
            description = 'Позволяет пользователю выйти из системы.')
        async def getAuthPage(request: Request) -> _TemplateResponse:
            return self['authLogout'].render(
                request
                )

        @self.api.get('/auth/login', response_class = HTMLResponse,
            name = 'Авторизация',
            description = 'Отрисовывает страницу авторизации.')
        async def getAuthPage(request: Request, to: str = '/') -> _TemplateResponse:
            return self['authLogin'].render(
                request,
                redirectAfter = to,
                version = str(version())
                )

        @self.api.get('/account', response_class = HTMLResponse,
            name = 'Аккаунт',
            description = 'Отрисовывает страницу своего аккаунта.')
        async def getSelfAccountPage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            return self['account'].render(
                request,
                user = user,
                thisAccount = user,
                accounts = self.auth.getUsers(),
                version = str(version())
                )

        @self.api.get('/account/{username}', response_class = HTMLResponse,
            name = 'Аккаунт',
            description = 'Отрисовывает страницу конкретного аккаунта.')
        async def getAccountPage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            return self['account'].render(
                request,
                user = user,
                thisAccount = self.auth.getUser,
                accounts = self.auth.getUsers(),
                version = str(version())
                )

        @self.api.get('/', response_class = HTMLResponse,
            name = 'Главная страница',
            description = 'Отрисовывает главную страницу с информацией о грядках.')
        async def getIndexPage(request: Request, user: Annotated[User, Depends(getUser)]) -> _TemplateResponse:
            self.logger.debug(f'Logged in as {user.username} with creds {[user.warden, user.master]}')
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

