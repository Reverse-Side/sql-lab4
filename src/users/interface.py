from typing import Protocol

from src.interface import IRepository
from src.mixin_schemas import Pagination, Collection
from src.users.schemas import UserResponce, UserUpdate


class IUser(Protocol):
    id: int
    username: str
    password: str
    email: str
    is_active: bool
    is_admin: bool


class IUserRepository(IRepository[IUser]):
    pass


class IUserService(Protocol):
    async def get(_id: int) -> UserResponce | None: ...
    async def update(_id: int, data: UserUpdate) -> UserResponce: ...
    async def get_list(pagin: Pagination) -> Collection[UserResponce]: ...
