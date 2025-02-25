from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.amenity.room_amenity.models import RoomAmenity, RoomAmenityAssociation
    from app.api.booking.models import Booking
    from app.api.hotel.models import Hotel
    from app.api.images.models import RoomImage


class BedType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    rooms: Mapped[list["Room"]] = relationship(back_populates="bed_type")


class RoomType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    # relationships
    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")


class Room(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    max_guests: Mapped[int] = mapped_column()
    max_children: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column(Text, nullable=True)
    preview_photo_url: Mapped[str] = mapped_column(String, nullable=True)
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
    )
    price_per_night: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    room_area: Mapped[float] = mapped_column(Float, nullable=True)
    # is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=5,
        server_default="5",
    )

    # relationships
    bed_type_id: Mapped[int] = mapped_column(ForeignKey("bed_types.id"))
    bed_type: Mapped["BedType"] = relationship(back_populates="rooms")
    room_type_id: Mapped["RoomType"] = mapped_column(ForeignKey("room_types.id"))
    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="room",
    )
    hotel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hotels.id"),
    )
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="rooms",
    )
    room_amenity_association: Mapped[list["RoomAmenityAssociation"]] = relationship(
        "RoomAmenityAssociation",
        back_populates="room",
    )
    room_amenities: Mapped[list["RoomAmenity"]] = relationship(
        secondary="room_amenity_associations",
        back_populates="rooms",
    )
    room_images: Mapped[list["RoomImage"]] = relationship(
        back_populates="room",
    )
