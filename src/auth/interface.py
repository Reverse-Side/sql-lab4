from typing import Generic, Protocol, TypeVar
from src.auth.schemas import (
    LogOutResponce,
    LoginResponce,
    TokenSchemas,
    UserLogin,
    UserRegister,
    TokenInfo,
)
from src.interface import ICreatedAt, IRepository

T = TypeVar("T")


class IRefreshToken(ICreatedAt, Protocol):
    id: int
    token: str
    user_id: int
    revoked: bool


class IRefreshTokenRepository(IRepository[IRefreshToken]):
    pass


class IAuthService(Protocol):
    async def login(self, data: UserLogin) -> LoginResponce: ...
    async def register(self, data: UserRegister) -> LoginResponce: ...
    async def refresh(self, token_refresh: str) -> TokenSchemas: ...
    async def logout(self, token_refresh: str) -> LogOutResponce: ...
    def auth(token: str) -> TokenInfo: ...
