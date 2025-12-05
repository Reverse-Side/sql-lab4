from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, FileUrl
from src.users.schemas import User


ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)


class LogOutResponce(BaseModel):
    revoked: str


class UserRegister(User, UserLogin):
    pass


class TokenSchemas(BaseModel):
    token: str
    type_token: str = Field(default="Bearer")


class TokenCreate(BaseModel):
    type: str
    sub: int
    username: str
    email: EmailStr
    is_admin: bool


class TokenInfo(TokenCreate):
    iat: datetime
    exp: datetime


class LoginResponce(BaseModel):
    access_token: TokenSchemas
    refresh_token: TokenSchemas
