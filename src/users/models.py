from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import RefreshTokenORM
from src.database import Base
from src.events.models import EventORM
from src.mixin_models import CreatedAtMixin
from src.payments.models import PaymentORM
from src.tickets.models import TicketsORM


class UserORM(Base, CreatedAtMixin):
    __tablename__ = "users"
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str]

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    tokens: Mapped[list["RefreshTokenORM"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    events: Mapped[list["EventORM"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    tickets: Mapped[list["TicketsORM"]] = relationship(
        "TicketsORM", back_populates="owner", cascade="all, delete-orphan"
    )
    payments: Mapped[list["PaymentORM"]] = relationship(
        "PaymentORM", back_populates="user", cascade="all, delete-orphan"
    )
