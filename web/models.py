# -*- coding: utf-8 -*-
from pydantic import BaseModel, constr
from typing   import Optional


class User(BaseModel):
    username: str
    enabled:  bool
    warden:   bool
    ruler:    Optional[bool]

class AccessibleUser(User):
    password: str
    _password: constr(
        min_length = 96,
        max_length = 96,
        strip_whitespace = True,
        to_upper = True,
        regex = r'\b[A-Fa-f0-9]{96}\b')

class Token(BaseModel):
    access_token: str
    token_type:   str

class TokenPair(BaseModel):
    access_token: str
    token_type:   str

class TokenData(BaseModel):
    username: str | None = None
    scopes:   str | None = None
