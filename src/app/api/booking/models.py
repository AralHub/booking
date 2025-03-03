from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    text,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models import Room
    from app.api.user.models import User


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Booking(IntIdPkMixin, Base):
    check_in_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )
    check_out_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )
    status: Mapped[BookingStatus] = mapped_column(
        SqlEnum(BookingStatus),
        nullable=False,
        default=BookingStatus.PENDING,
        server_default=text("'PENDING'"),
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    guest_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    # relationships
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["Room"] = relationship("Room", back_populates="bookings")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    __table_args__ = (
        CheckConstraint(
            "check_in_date < check_out_date",
            name="check_in_date_before_check_out_date",
        ),
    )
