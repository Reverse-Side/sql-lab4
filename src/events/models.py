from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import get_base_class
from src.mixin_models import CreatedAtMixin
from datetime import datetime

Base = get_base_class()
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.users.models import UserORM
    from src.tickets.models import TicketsORM
    from src.seats.models import SeatsORM

class EventORM(Base, CreatedAtMixin):
    __tablename__ = "events"
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str]
    description: Mapped[str | None]
    location: Mapped[str]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]

    owner: Mapped["UserORM"] = relationship(back_populates="events")
    tickets: Mapped[list["TicketsORM"]] = relationship(
        "TicketsORM",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    seats: Mapped[list["SeatsORM"]] = relationship(
        back_populates="event")