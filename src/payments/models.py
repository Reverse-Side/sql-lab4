from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.mixin_models import CreatedAtMixin

if TYPE_CHECKING:
    from src.tickets.models import TicketsORM
    from src.users.models import UserORM


class PaymentORM(Base, CreatedAtMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(nullable=False)
    payment_method: Mapped[str] = mapped_column(nullable=False)
    payment_status: Mapped[str] = mapped_column(nullable=False)
    payment_date: Mapped[datetime] = mapped_column(nullable=False)

    ticket: Mapped["TicketsORM"] = relationship(back_populates="payment", uselist=False)
    user: Mapped["UserORM"] = relationship(back_populates="payments")
