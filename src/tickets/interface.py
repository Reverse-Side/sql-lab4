

from typing import Protocol

from src.interface import IRepository


class ITickets(Protocol):
    owner_id: int
    event_id: int
    ticket_type: str
    price: int
    status: str
    is_used: bool

class ITicketsRepository(IRepository[ITickets]):
    pass