from fastapi import Depends
from src.filter import eq
from src.interface import IUnitOfWork
from src.mixin_schemas import Collection, Pagination
from src.unit_of_work import get_unit_of_work
from src.users.interface import IUserService
from src.users.schemas import UserResponce, UserUpdate


class UserService(IUserService):
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get(self, _id: int):
        async with self.uow as work:
            user = await work.users.find(id=eq(_id))
            if user:
                return UserResponce.model_validate(user)
            return user

    async def update(self, _id, data: UserUpdate):
        async with self.uow as work:
            user = await work.users.update(
                _id=_id, data=data.model_dump(exclude_unset=True)
            )
            if user:
                return UserResponce.model_validate(user)
            return user

    async def get_list(self, pagin: Pagination):
        async with self.uow as work:
            users = await work.users.find_all(offset=pagin.offset, limit=pagin.limit)
            users = list(map(lambda x: UserResponce.model_validate(x), users))
            return Collection(
                collection=users,
                offset=pagin.offset,
                limit=pagin.limit,
                size=len(users),
            )


def get_service():
    return UserService(uow=get_unit_of_work())
