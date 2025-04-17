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
    String,
    Text,
    text,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.room import Room
    from app.models.user import User
    from app.models.payment import PaymentMethod


class BookingStatus(str, Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingType(str, Enum):
    PERSONAL = "personal"
    BUSINESS = "business"


class BookedRoom(IntIdPkMixin, Base):
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    guest_name: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default=None,
        server_default=None,
    )
    guest_quantity: Mapped[int] = mapped_column(Integer)
    room_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    booking: Mapped["Booking"] = relationship("Booking", back_populates="booking_rooms")
    room: Mapped["Room"] = relationship("Room", back_populates="booking_rooms")


class Booking(
    IntIdPkMixin,
    TimestampMixin,
    Base,
):
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
        default=BookingStatus.BOOKED,
        server_default=text("'BOOKED'"),
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    total_guests: Mapped[int] = mapped_column(Integer, nullable=False)
    special_requests: Mapped[str] = mapped_column(Text, nullable=True)
    time: Mapped[str] = mapped_column(
        String,
        nullable=True,
        default=None,
        server_default=None,
    )
    payment_method_id: Mapped[int] = mapped_column(ForeignKey("payment_methods.id"))
    payment_method: Mapped["PaymentMethod"] = relationship(
        "PaymentMethod",
        back_populates="bookings",
    )
    booking_type: Mapped[BookingType] = mapped_column(
        SqlEnum(BookingType),
        nullable=False,
        default=BookingType.PERSONAL,
        server_default=text("'PERSONAL'"),
    )
    # relationships
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    booking_rooms: Mapped[list["BookedRoom"]] = relationship(
        "BookedRoom",
        back_populates="booking",
        cascade="all, delete-orphan",
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    __table_args__ = (
        CheckConstraint(
            "check_in_date < check_out_date",
            name="check_in_date_before_check_out_date",
        ),
        CheckConstraint(
            "(booking_type = 'PERSONAL') OR (booking_type = 'BUSINESS' AND company_id IS NOT NULL)",
            name="business_booking_must_have_company",
        ),
    )
