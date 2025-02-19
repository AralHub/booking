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


class AmenityCategory(IntIdPkMixin, Base):
    __tablename__ = "amenity_categories"
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    amenities: Mapped[list["Amenity"]] = relationship(
        back_populates="amenity_category",
    )


class Amenity(IntIdPkMixin, Base):
    __tablename__ = "amenities"
    name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    is_popular: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    payment_type: Mapped[PaymentType] = mapped_column(
        SqlEnum(PaymentType), default=PaymentType.FREE
    )
    amenity_category_id: Mapped[int] = mapped_column(
        ForeignKey("amenity_categories.id"),
    )
    amenity_category: Mapped[AmenityCategory] = relationship(
        back_populates="amenities",
    )
    hotel_association: Mapped[list["HotelAmenityAssociation"]] = relationship(
        "HotelAmenityAssociation",
        back_populates="amenity",
        cascade="all, delete-orphan",
    )
    hotels: Mapped[list["Hotel"]] = relationship(
        secondary="hotel_amenity_association",
        back_populates="amenities",
    )


class HotelAmenityAssociation(Base):
    __tablename__ = "hotel_amenity_association"
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id"),
        primary_key=True,
    )
    amenity_id: Mapped[int] = mapped_column(
        ForeignKey("amenities.id"),
        primary_key=True,
    )
    # association between Assocation -> Hotel
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="amenity_association",
    )
    # association between Assocation -> Amenity
    amenity: Mapped[Amenity] = relationship(
        "Amenity",
        back_populates="hotel_association",
    )
    __table_args__ = (
        UniqueConstraint(
            "hotel_id",
            "amenity_id",
            name="uq_hotel_amenity",
        ),
    )
