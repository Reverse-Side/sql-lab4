from src.repository import RepositoryORM
from src.events.models import EventORM 
#from sqlalchemy.ext.asyncio import AsyncSession


class EventRepository(RepositoryORM[EventORM]):
    model = EventORM
    pass