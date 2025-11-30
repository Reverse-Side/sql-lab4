from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SeatBase(BaseModel):
    event_id: int
    seat_row: str
    seat_number: str
    price: float



class SeatCreate(SeatBase):
    pass



class SeatResponse(BaseModel):
    id: int
    is_reserved: bool  
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)