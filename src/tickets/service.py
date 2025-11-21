from typing import Annotated, List

from fastapi import Depends, HTTPException, status

from src.exceptions import EntityNotFoundError, IntegrityRepositoryError
from src.filter import eq
from src.interface import IUnitOfWork
from src.tickets.schemas import TicketCreate, TicketResponse
from src.unit_of_work import get_unit_of_work


class TicketService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def create_ticket(self, ticket_data: TicketCreate, owner_id: int) -> TicketResponse:
        async with self.uow as work:
            event = await work.events.find(id=eq(ticket_data.event_id))
            if not event:
                raise EntityNotFoundError(f"Event with id {ticket_data.event_id} not found")

            data_to_add = ticket_data.model_dump()
            data_to_add["owner_id"] = owner_id
            
            try:
                new_ticket = await work.tickets.add(data=data_to_add)
                await work.commit()
                return TicketResponse.model_validate(new_ticket)
            except IntegrityRepositoryError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket already exists")
            
    async def get_tickets_by_owner(self, owner_id: int) -> List[TicketResponse]:
        async with self.uow as work:
            tickets = await work.tickets.find_all(owner_id=eq(owner_id))
            return [TicketResponse.model_validate(ticket) for ticket in tickets]
        
    async def get_tickets_by_id(self, ticket_id: int) -> TicketResponse:
        async with self.uow as work:
            ticket = await work.tickets.find(id=eq(ticket_id))
            if not ticket:
                raise EntityNotFoundError(f"Ticket with id {ticket_id} not found")
            return TicketResponse.model_validate(ticket)


def get_ticket_service(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]):
    return TicketService(uow)


TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]