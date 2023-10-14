# -*- coding: utf-8 -*-
class UsernameNotFoundException(Exception):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f'Пользователь {username} не существует')


class UserDisabledException(Exception):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(
            f'Профиль пользователя {username} не может '
            'быть использован, так как он отключен')


class UserPasswordException(Exception):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(
            f'Пароль пользователя {username} неверен')


class TokenExpirationException(Exception):
    def __init__(self) -> None:
        super().__init__(
            'Токен оказался истекшим.')
