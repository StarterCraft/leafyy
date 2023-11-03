# -*- coding: utf-8 -*-
from datetime    import datetime, timedelta
from autils      import fread, fwrite

from secrets     import token_hex
from hashlib     import pbkdf2_hmac
from jose        import JWTError
from jose.jwt    import encode as jwtenc, decode as jwtdec
from fastapi.security import OAuth2PasswordRequestForm

from leafyy      import postgres

from .models     import User, AccessibleUser, TokenPair
from .exceptions import *


ALGORITHM = 'HS384'
ACCESS_TOKEN_EXPIRATION_MINUTES = 30
REFRESH_TOKEN_EXPIRATION_DAYS = 30
SALT_MULTIPLIER = 381
USE_BCRYPT = False
HMAC_ITERATIONS = 880738


class LeafyyAuthentificator:
    def getSalt(self) -> str:
        salt = ''
        try:
            salt = fread('web/upsalt.token').lower()
            if (not salt):
                salt = token_hex(48)
                fwrite('web/upsalt.token', token_hex(48))
            return salt
        except (FileNotFoundError, PermissionError):
            salt = token_hex(48)
            fwrite('web/upsalt.token', token_hex(48))
            return salt

    if (USE_BCRYPT):
        from passlib.context import CryptContext

        bcrypt = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

        def checkPassword(self, username: str, plain: str, encoded: str) -> bool:
            try:
                pass#return bcrypt.verify(plain, encoded)
            except Exception as e:
                raise UserPasswordException(username) from e
    else:
        def checkPassword(self, username: str, plain: str, encoded: str) -> bool:
            try:
                h = pbkdf2_hmac(
                    'sha384',
                    plain.encode('utf-8'),
                    self.getSalt().encode('utf-8') * SALT_MULTIPLIER,
                    HMAC_ITERATIONS
                    ).hex()
                print('H' * 38, '\n', h)
                return h == encoded
            except Exception as e:
                raise UserPasswordException(username) from e

    def selectUser(self, username: str, verifyOnly: bool = False) -> AccessibleUser | None:
        thisUser = postgres().fetchone('web.selectUser', username)

        if (not thisUser):
            raise UsernameNotFoundException(username)
        elif (not thisUser.enabled):
            raise UserDisabledException(username)
        else:
            if (not verifyOnly):
                return AccessibleUser(**thisUser._asdict())

    def getUsers(self) -> list[User]:
        ud = postgres().fetchall('web.selectUsers')

        return [User(**d._asdict()) for d in ud]

    def authenticateUser(self, username: str, password: str) -> AccessibleUser:
        user = self.selectUser(username)
        if (self.checkPassword(username, password, user.password)):
            return user
        else:
            raise UserPasswordException(username)

    def resolveUser(self, token: str, verifyOnly: bool = False) -> AccessibleUser | None:
        payload = jwtdec(token, self.getSalt(), algorithms = [ALGORITHM])
        if (datetime.utcnow().timestamp() > payload['expires']):
            print(datetime.utcnow().timestamp() > payload['expires'], datetime.utcnow().timestamp(), payload['expires'])

            raise TokenExpirationException
        username: str = payload['user']
        return self.selectUser(username, verifyOnly = verifyOnly)

    def createAccessToken(self, data: dict) -> str:
        toEncode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRATION_MINUTES)
        print(expire)
        toEncode.update({"expires": expire.timestamp()})
        encodedJwt = jwtenc(toEncode, self.getSalt(), algorithm = ALGORITHM)
        return encodedJwt

    def createRefreshToken(self, data: dict) -> str:
        toEncode = data.copy()
        expire = datetime.utcnow() + timedelta(days = REFRESH_TOKEN_EXPIRATION_DAYS)
        print(expire)
        toEncode.update({"refresh": True, "expires": expire.timestamp()})
        encodedJwt = jwtenc(toEncode, self.getSalt(), algorithm = ALGORITHM)
        return encodedJwt

    def getAccessToken(self, formData: OAuth2PasswordRequestForm) -> TokenPair:
        user = self.authenticateUser(formData.username, formData.password)
        accessToken = self.createAccessToken({"user": user.username})
        refreshToken = self.createRefreshToken({"user": user.username})
        return {'access_token': accessToken, 'refresh_token': refreshToken, 'token_type': 'bearer'}

    def getRefreshToken(self, refreshToken: str) -> TokenPair:
        payload = jwtdec(refreshToken, self.getSalt(), algorithms = [ALGORITHM])
        if (datetime.utcnow().timestamp() > payload['expires']):
            print(datetime.utcnow().timestamp() > payload['expires'], datetime.utcnow().timestamp(), payload['expires'])
            raise TokenExpirationException()
        username: str = payload['user']
        self.selectUser(username, verifyOnly = True)
        accessToken = self.createAccessToken({"sub": username})
        refreshToken = self.createRefreshToken({"sub": username})
        return {'access_token': accessToken, 'refresh_token': refreshToken, 'token_type': 'bearer'}
