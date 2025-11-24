from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Float, DateTime
from src.database import get_base_class
from src.mixin_models import CreatedAtMixin 
from typing import TYPE_CHECKING
from datetime import datetime

Base = get_base_class()


if TYPE_CHECKING:
    from src.users.models import UserORM
    from src.tickets.models import TicketsORM

class PaymentORM(Base, CreatedAtMixin):
    __table_name__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    payment_status: Mapped[str] = mapped_column(String, nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    ticket: Mapped["TicketsORM"] = relationship(back_populates='payment', uselist=False)
    user: Mapped["UserORM"] = relationship(back_populates='payments')
