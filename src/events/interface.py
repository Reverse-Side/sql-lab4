from datetime import datetime
from typing import Protocol
from src.interface import ICreatedAt, IRepository
class IEvent(ICreatedAt,Protocol):
    id:int
    owner_id:int
    title:str|None
    location:str
    date_time:datetime
    
class IEventRepository(IRepository[IEvent]):
    pass