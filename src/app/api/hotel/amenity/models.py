from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models import Hotel


class PaymentType(str, Enum):
    FREE = "free"
    PAID = "paid"
    PAID_SEPARATELY = "paid_separately"


class HotelAmenityCategory(IntIdPkMixin, Base):
    __tablename__ = "hotel_amenity_categories"
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    hotel_amenities: Mapped[list["HotelAmenity"]] = relationship(
        back_populates="hotel_amenity_category",
    )


class HotelAmenity(IntIdPkMixin, Base):
    __tablename__ = "hotel_amenities"
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    is_popular: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    payment_type: Mapped[PaymentType] = mapped_column(
        SqlEnum(PaymentType),
        default=PaymentType.FREE,
    )
    hotel_amenity_category_id: Mapped[int] = mapped_column(
        ForeignKey("hotel_amenity_categories.id"),
    )
    hotel_amenity_category: Mapped[HotelAmenityCategory] = relationship(
        back_populates="hotel_amenities",
    )
    hotel_association: Mapped[list["HotelAmenityAssociation"]] = relationship(
        "HotelAmenityAssociation",
        back_populates="hotel_amenity",
        cascade="all, delete-orphan",
    )
    hotels: Mapped[list["Hotel"]] = relationship(
        secondary="hotel_amenity_association",
        back_populates="hotel_amenities",
    )


class HotelAmenityAssociation(Base):
    __tablename__ = "hotel_amenity_association"
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id"),
        primary_key=True,
    )
    hotel_amenity_id: Mapped[int] = mapped_column(
        ForeignKey("hotel_amenities.id"),
        primary_key=True,
    )
    # association between Assocation -> Hotel
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="amenity_association",
    )
    # association between Assocation -> Amenity
    hotel_amenity: Mapped[HotelAmenity] = relationship(
        "HotelAmenity",
        back_populates="hotel_association",
    )
    __table_args__ = (
        UniqueConstraint(
            "hotel_id",
            "hotel_amenity_id",
            name="uq_hotel_amenity",
        ),
    )


class RoomAmenityCategory(IntIdPkMixin, Base):
    __tablename__ = "room_amenity_categories"
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    room_amenities: Mapped[list["RoomAmenity"]] = relationship(
        back_populates="room_amenity_category",
    )


class RoomAmenity(IntIdPkMixin, Base):
    __tablename__ = "room_amenities"
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    room_amenity_category_id: Mapped[int] = mapped_column(
        ForeignKey("room_amenity_categories.id"),
    )
    room_amenity_category: Mapped[RoomAmenityCategory] = relationship(
        back_populates="room_amenities",
    )
