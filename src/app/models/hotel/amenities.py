from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import (
    IntIdPkMixin,
    MultilingualNameMixin,
)

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class PaymentType(str, Enum):
    FREE = "free"
    PAID = "paid"


class HotelAmenityCategory(
    IntIdPkMixin,
    MultilingualNameMixin,
    Base,
):
    __tablename__ = "hotel_amenity_categories"

    hotel_amenities: Mapped[list["HotelAmenity"]] = relationship(
        back_populates="hotel_amenity_category",
        cascade="all, delete-orphan",
    )


class HotelAmenity(
    IntIdPkMixin,
    MultilingualNameMixin,
    Base,
):
    icon: Mapped[str] = mapped_column(
        String,
        nullable=True,
        default=None,
        server_default=None,
        unique=True,
    )
    in_hotel: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=True,
        server_default="true",
    )
    is_popular: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
    )
    payment_type: Mapped[PaymentType] = mapped_column(
        SqlEnum(PaymentType),
        default=PaymentType.FREE,
        server_default=text("'FREE'"),
    )
    hotel_amenity_category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "hotel_amenity_categories.id",
            ondelete="CASCADE",
        ),
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
        secondary="hotel_amenity_associations",
        back_populates="hotel_amenities",
    )


class HotelAmenityAssociation(Base):
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id"),
        primary_key=True,
    )
    hotel_amenity_id: Mapped[int] = mapped_column(
        ForeignKey("hotel_amenities.id"),
        primary_key=True,
    )
    # association between Assocation -> Hotelw
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="hotel_amenity_association",
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
