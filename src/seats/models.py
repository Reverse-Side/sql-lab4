from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, Float
from src.database import get_base_class 
from src.mixin_models import CreatedAtMixin 
from typing import TYPE_CHECKING

Base = get_base_class()


if TYPE_CHECKING:
    from src.events.models import EventORM
    from src.tickets.models import TicketsORM 


class SeatsORM(Base, CreatedAtMixin):
    __tablename__ = "seats"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id'))
    seat_number: Mapped[str] = mapped_column(String, nullable=False)
    is_reserved: Mapped[bool] = mapped_column(Boolean, default=False)
    seat_row = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    event: Mapped["EventORM"] = relationship(back_populates='seats')
    ticket: Mapped["TicketsORM"] = relationship(back_populates='seat', uselist=False)