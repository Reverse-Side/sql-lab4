from typing import Any, Callable, TypeVar
from sqlalchemy import Result, Select, Tuple, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import StatementError, IntegrityError, SQLAlchemyError

from src.database import Base
from src.exceptions import IntegrityRepositoryError, InvalidQueryError, RepositoryError
from src.filter import Filter, FilterHeadler, Op
from src.interface import IRepository
from typing import TypeVar, Generic

from src.users.models import UserORM
from src.auth.models import RefreshTokenORM  
from src.events.models import EventORM
from src.tickets.models import TicketsORM


def execute(func: Callable):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            raise IntegrityRepositoryError(f"Integrity error during DB operation: {e}") from e
        except StatementError as e:
            raise InvalidQueryError(f"Invalid query or filter: {e}") from e

    return wrapper


T = TypeVar("T", bound=Base)


class RepositoryORM(Generic[T]):
    model: type[T] = None

    def __init__(self, session: AsyncSession):
        if self.model is None:
            raise NotImplementedError("Repository must specify a model class.")
        self.session = session
        self._filter = FilterHeadler(self.model)

    @execute
    async def find_all(self, limit=10, offset=0, filter: Filter = Filter(), **filters):
        stmt = await self.__find(_filter=filter, filters=filters)
        stmt = stmt.offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    @execute
    async def find(
        self,
        filter: Filter = Filter(),
        **filters: Op,
    ):

        stmt = await self.__find(_filter=filter, filters=filters)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    @execute
    async def add(self, data) -> T:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    @execute
    async def update(self, _id: int, data: dict):
        stmt = (
            update(self.model)
            .where(self.model.id == _id)
            .values(**{k: v for k, v in data.items() if k != "id"})
            .returning(self.model)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    @execute
    async def delete(self, _id: int):
        stmt = delete(self.model).where(self.model.id == _id).returning(self.model)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.scalar_one_or_none()

    async def __find(self, _filter: Filter, filters: dict[str, Any]) -> Select[Tuple]:
        stmt = select(self.model)
        f = self._resolve_filter(_filter, filters)
        stmt = stmt.where(*f)
        return stmt

    def _resolve_filter(self, _filter: Filter, _filters: dict) -> list[Callable]:
        if not isinstance(_filter, Filter):
            raise TypeError(f"_filter must be Filter, not {type(_filter)}")
        _filter.overload(**_filters)
        return self._filter.to_conditions(_filter)

class EventRepository(RepositoryORM[EventORM]):
    model = EventORM  

class TicketRepository(RepositoryORM[TicketsORM]):
    model = TicketsORM 