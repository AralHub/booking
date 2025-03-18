from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.hotel import Hotel
    from app.models.room.amenities import RoomAmenity, RoomAmenityAssociation
    from app.models.room.bed import RoomBedConfiguration
    from app.models.room.images import RoomImage
    from app.models.room.price import RoomPrice
    from app.models.room.types import RoomType


class Room(IntIdPkMixin, Base):
    max_guests: Mapped[int] = mapped_column(
        nullable=False,
        default=1,
        server_default="1",
    )
    image: Mapped[str] = mapped_column(String, nullable=True)
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
    )
    base_price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    room_area: Mapped[float] = mapped_column(Float, nullable=True)
    use_dinamic_price: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        server_default="false",
    )
    # relationships
    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))
    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")
    # bookings: Mapped[list["Booking"]] = relationship(
    #     "Booking",
    #     back_populates="room",
    # )
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
