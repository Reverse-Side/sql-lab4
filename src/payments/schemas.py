from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class PaymentCreate(BaseModel):
    ticket_id: int = Field(..., description="ID квитка")
    amount: float = Field(..., description="Сума оплати")
    payment_method: str = Field(..., description="Метод оплати")


class PaymentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    amount: float
    payment_method: str
    payment_status: str
    payment_date: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PaymentStatusUpdate(BaseModel):
    payment_status: str


