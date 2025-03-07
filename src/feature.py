from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin, TimestampMixin

if TYPE_CHECKING:
    from app.api.amenity.hotel_amenity.models import (
        HotelAmenity,
        HotelAmenityAssociation,
    )
    from app.api.hotel_admin.models import HotelAdmin, HotelAdminInfo
    from app.api.images.models import HotelImage
    from app.api.locations.models import Location
    from app.api.review.models import Review
    from app.api.room.models import Room
    from app.api.rule.models import Rule


class HotelCategory(IntIdPkMixin, Base):
    __tablename__ = "hotel_categories"
    name: Mapped[str] = mapped_column(String(255), unique=True)
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel",
        back_populates="hotel_category",
    )


class Hotel(IntIdPkMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    image: Mapped[str] = mapped_column(String, nullable=True)

    # relationships
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="hotel",
        cascade="all, delete-orphan",
    )
    hotel_category_id: Mapped[int] = mapped_column(
        ForeignKey("hotel_categories.id"),
    )
    hotel_category: Mapped["HotelCategory"] = relationship(
        "HotelCategory",
        back_populates="hotels",
    )
    hotel_amenity_association: Mapped[list["HotelAmenityAssociation"]] = relationship(
        "HotelAmenityAssociation",
        back_populates="hotel",
    )
    hotel_amenities: Mapped[list["HotelAmenity"]] = relationship(
        secondary="hotel_amenity_associations",
        back_populates="hotels",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="hotel",
    )
    location: Mapped["Location"] = relationship(
        "Location",
        uselist=False,
        single_parent=True,
    )
    hotel_images: Mapped[list["HotelImage"]] = relationship(
        "HotelImage",
        back_populates="hotel",
    )
    rule: Mapped["Rule"] = relationship(
        "Rule",
        back_populates="hotel",
    )
    hotel_admin: Mapped["HotelAdmin"] = relationship(back_populates="hotel")
    hotel_admin_info: Mapped["HotelAdminInfo"] = relationship(back_populates="hotel")
    # languages: Mapped[list["Language"]] = relationship(
    #     secondary="hotel_language_associations",
    #     back_populates="hotels",
    # )


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


class RoomTypeVariant(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))
    room_type: Mapped["RoomType"] = relationship(back_populates="room_type_variants")
    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type_variant")


class RoomType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    # relationships
    # rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")
    room_type_variants: Mapped[list["RoomTypeVariant"]] = relationship(
        back_populates="room_type"
    )


class RoomPrice(IntIdPkMixin, Base):
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    guest_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    room: Mapped["Room"] = relationship(back_populates="room_prices")


class Room(IntIdPkMixin, Base):
    max_guests: Mapped[int] = mapped_column(nullable=True)
    max_children: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
    )
    base_price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    room_area: Mapped[float] = mapped_column(Float, nullable=True)
    # is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # relationships
    room_type_variant_id: Mapped[int] = mapped_column(
        ForeignKey("room_type_variants.id")
    )
    room_type_variant: Mapped["RoomTypeVariant"] = relationship(back_populates="rooms")
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
