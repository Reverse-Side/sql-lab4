from typing import List, Annotated
from fastapi import Depends, HTTPException, status
from src.seats.schemas import SeatCreate, SeatResponse
from src.seats.models import SeatsORM 
from src.unit_of_work import get_unit_of_work
from src.filter import eq 
from src.exceptions import EntityNotFoundError, IntegrityRepositoryError
from src.interface import IUnitOfWork


class SeatService:
    def __init__(self, uow:IUnitOfWork):
        self.uow = uow

    async def add_seat(self, seat_date: SeatCreate) -> SeatResponse:
        async with self.uow as work:
            event = await work.events.find(id = eq(seat_date.event_id))
            if not event:
                raise EntityNotFoundError(f"Event with id {seat_date.event_id} not found")
            
            data_to_add = seat_date.model_dump()

            try:
                new_seat = await work.seats.add(data=data_to_add)
                await work.commit()
                return SeatResponse.model_validate(new_seat)
            except IntegrityRepositoryError:
               raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Seat with this row and number already exists for this event."
                )
    async def get_available_seats(self, event_id: int) -> List[SeatResponse]:
        async with self.uow as work:
            seats = await work.seats.filter(
                event_id=eq(event_id),
                is_reserved=eq(False)
            )
            return [SeatResponse.model_validate(seat) for seat in seats]
        
    async def reserve_seat(self, seat_id: int, commit: bool = True) -> SeatResponse:
        async with self.uow as work:
            seat = await work.seats.find(id=eq(seat_id))
            if not seat:
                raise EntityNotFoundError(f"Seat with id {seat_id} not found")
            if seat.is_reserved:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Seat is already reserved."
                )
            updated_seat_orm = await work.seats.update(
                id=seat_id,
                data={"is_reserved": True}
            )
            
            if commit:
                await work.commit()
                
            return SeatResponse.model_validate(updated_seat_orm)




def get_seat_service(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]):
    """Фабрична функція для створення SeatService"""
    return SeatService(uow)


SeatServiceDep = Annotated[SeatService, Depends(get_seat_service)]