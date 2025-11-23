from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.mixin_models import CreatedAtMixin



class TicketsORM(Base, CreatedAtMixin):
    __tablename__ = "tickets"
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    ticket_type: Mapped[str] = mapped_column(default="Standart")
    price: Mapped[int]
    status: Mapped[str] = mapped_column(default="reserved")
    is_used: Mapped[bool] = mapped_column(default=False)
    seat_id: Mapped[int | None] = mapped_column(ForeignKey("seats.id"), unique=True)

    event = relationship("EventORM", back_populates="tickets")
    owner = relationship("UserORM", back_populates="tickets")
    seat = relationship("SeatsORM", back_populates="ticket")
