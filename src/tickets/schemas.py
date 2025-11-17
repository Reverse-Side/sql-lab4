from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TicketBase(BaseModel):
    event_id: int
    ticket_type: str = "Standart"
    price: int


class Config:
    from_attributes = True

class TicketCreate(TicketBase):
    pass
class TicketResponse(TicketBase):
    id: int
    owner_id: int
    is_used: bool
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)