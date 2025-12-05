import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.auth.repository import RefreshTokenRepository
from src.database import new_async_session
from src.events.repository import EventRepository
from src.interface import IUnitOfWork
from src.tickets.repository import TicketsRepository
from src.users.repository import UserRepository
from src.seats.repository import SeatsRepository

log = logging.getLogger(__name__)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory
        self.users: UserRepository
        self.refresh_tokens: RefreshTokenRepository
        self.events: EventRepository
        self.tickets: TicketsRepository
        self.seats: SeatsRepository

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.users = UserRepository(self.session)
        self.refresh_tokens = RefreshTokenRepository(self.session)
        self.events = EventRepository(self.session)
        self.tickets = TicketsRepository(self.session)
        self.seats = SeatsRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                # Якщо exc_type не є None, це означає, що у блоці 'async with'
                # виникла помилка. Ми викликаємо ROLLBACK.
                log.error("Rollback")
                await self.rollback()
            else:
                # Якщо помилки не було, викликаємо COMMIT.
                log.info("Commit")
                await self.commit()
        finally:
            # Сесія має бути закрита незалежно від результату
            log.info("Cloce db")
            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


def get_unit_of_work():
    return SqlAlchemyUnitOfWork(new_async_session)
