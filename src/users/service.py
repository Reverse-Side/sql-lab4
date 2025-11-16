from fastapi import Depends
from src.filter import eq
from src.interface import IUnitOfWork
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


def get_service():
    return UserService(uow=get_unit_of_work())
