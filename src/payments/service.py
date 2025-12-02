from datetime import datetime
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status

from src.interface import IUnitOfWork
from src.payments.schemas import PaymentCreate, PaymentResponse, PaymentStatusUpdate
from src.tickets.models import TicketsORM
from src.unit_of_work import get_unit_of_work


class PaymentService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def process_payment(
        self, data: PaymentCreate, user_id: int
    ) -> PaymentResponse:
        async with self.uow:
            ticket: Optional[TicketsORM] = await self.uow.tickets.find(
                id=data.ticket_id
            )
            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
                )
            if ticket.is_paid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ticket already paid",
                )
            if data.amount <= ticket.price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough funds"
                )
            if ticket.owner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this ticket",
                )

            payment_data = {
                "ticket_id": data.ticket_id,
                "user_id": user_id,
                "amount": data.amount,
                "payment_method": data.payment_method,
                "payment_status": "success",
                "payment_data": datetime.utcnow(),
            }
            new_payment = await self.uow.payments.add(data=payment_data)

            await self.uow.tickets.update(id=data.ticket_id, data={"is_paid": True})
            await self.uow.commit()
            return new_payment

    async def update_payment_status(
        self, payment_id: int, status_data: PaymentStatusUpdate
    ) -> PaymentResponse:
        async with self.uow:
            updated_payment = await self.uow.update(
                _id=payment_id, data=status_data.model_dump(exclude_unset=True)
            )

        if updated_payment.payment_status == "success":
            ticket = await self.uow.tickets.find(id=updated_payment.ticket_id)
            if ticket and not ticket.is_paid:
                await self.uow.tickets.update(_id=ticket.id, data={"is_paid": True})
                await self.uow.commit()
                return updated_payment


def get_payment_service(uow: IUnitOfWork = Depends(get_unit_of_work)):
    return PaymentService(uow)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
