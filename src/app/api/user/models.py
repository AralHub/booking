from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin, TimestampMixin

if TYPE_CHECKING:
    from app.api.booking.models import Booking


class User(IntIdPkMixin, TimestampMixin, Base):
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    birthday: Mapped[datetime] = mapped_column(Date)
    phone_number: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=True,
        default=None,
        server_default=None,
    )
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    is_fully_registered: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    is_active: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    # relationships
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class TokenBlacklist(IntIdPkMixin, Base):
    jti: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
    )
    is_blacklisted: Mapped[bool] = mapped_column(
        default=True,
        server_default="true",
    )
