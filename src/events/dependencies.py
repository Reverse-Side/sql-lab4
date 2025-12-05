from typing import Annotated
from fastapi import Depends
from src.unit_of_work import get_unit_of_work 
from .service import EventService 
from src.tickets.service import TicketServiceDep
from src.interface import IUnitOfWork

def get_event_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    ticket_service: TicketServiceDep 
) -> EventService:
    """Тут відбувається впровадження залежностей EventService.""" 
    
    return EventService(uow=uow, ticket_service=ticket_service)

EventServiceDep = Annotated[EventService, Depends(get_event_service)]