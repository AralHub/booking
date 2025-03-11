from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.hotel import Hotel
    from app.models.room.amenities import RoomAmenity, RoomAmenityAssociation
    from app.models.room.images import RoomImage


class BedType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    room_bed_configs: Mapped[list["RoomBedConfiguration"]] = relationship(
        back_populates="bed_type"
    )


class RoomBedConfiguration(IntIdPkMixin, Base):
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    bed_type_id: Mapped[int] = mapped_column(ForeignKey("bed_types.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    # relationships
    room: Mapped["Room"] = relationship(back_populates="bed_configurations")
    bed_type: Mapped["BedType"] = relationship(back_populates="room_bed_configs")


class RoomType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    # relationships
    # rooms: Mapped`[list["Room"]] = relationship(back_populates="room_type")
    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")


class RoomPrice(IntIdPkMixin, Base):
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    guest_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    room: Mapped["Room"] = relationship(back_populates="room_prices")


class Room(IntIdPkMixin, Base):
    max_guests: Mapped[int] = mapped_column(nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
    )
    base_price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    room_area: Mapped[float] = mapped_column(Float, nullable=True)

    # relationships
    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))
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
    bed_configurations: Mapped[list["RoomBedConfiguration"]] = relationship(
        "RoomBedConfiguration", back_populates="room"
    )
    room_prices: Mapped[list["RoomPrice"]] = relationship(
        "RoomPrice",
        back_populates="room",
    )
