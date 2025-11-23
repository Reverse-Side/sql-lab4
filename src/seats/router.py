from fastapi import APIRouter, status, Depends
from typing import List, Annotated
from src.seats.schemas import SeatCreate, SeatResponse
from src.seats.service import SeatServiceDep


router = APIRouter(
    prefix="/seats",
    tags=["Seats"]
)

@router.post("/", response_model=SeatResponse, status_code=status.HTTP_201_CREATED, summary="Add a new seat to an event (Admin only)")
async def add_seat(seat_data: SeatCreate, seat_service: SeatServiceDep):
    return await seat_service.add_seat(seat_data)

@router.get("/avialable", response_model=List[SeatResponse], summary="Get available seats for an event (Admin only)") 
async def get_available_seats(event_id: int, seat_service: SeatServiceDep):
    return await seat_service.get_available_seats(event_id)