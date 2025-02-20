from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.booking.models import Booking

    from ..models import Hotel


class RoomType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))

    # relationships
    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")
    # room_amenities: Mapped[list["RoomAmenity"]] = relationship(back_populates="room_type")


class BedType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    max_capacity: Mapped[int] = mapped_column()


class Room(IntIdPkMixin, Base):
    max_guests: Mapped[int] = mapped_column()
    max_children: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column(Text, nullable=True)
    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=5,
        server_default="5",
    )
    preview_photo_path: Mapped[str] = mapped_column(String, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    price_per_night: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    # quantity: Mapped[int] = mapped_column(Integer, default=0)
    # relationships

    room_type_id: Mapped["RoomType"] = mapped_column(ForeignKey("room_types.id"))
    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")

    booking: Mapped["Booking"] = relationship(back_populates="room")
    hotel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "hotels.id",
            ondelete="CASCADE",
        ),
    )
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="rooms",
    )
