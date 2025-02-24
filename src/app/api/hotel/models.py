from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.amenity.hotel_amenity.models import (
        HotelAmenity,
        HotelAmenityAssociation,
    )
    from app.api.images.models import Image
    from app.api.locations.models import Location
    from app.api.review.models import Review  # noqa
    from app.api.room.models import Room
    from app.api.rule.models import Rule


class HotelCategory(IntIdPkMixin, Base):
    __tablename__ = "hotel_categories"
    name: Mapped[str] = mapped_column(String(255), unique=True)
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel",
        back_populates="hotel_category",
    )


class Hotel(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    # slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    # rooms_quantity: Mapped[int] = mapped_column(Integer, default=0)
    # relationships
    # admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

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
    # languages: Mapped[list["Language"]] = relationship(
    #     secondary="hotel_language_associations",
    #     back_populates="hotels",
    # )
    images: Mapped[list["Image"]] = relationship(
        "Image",
        back_populates="hotel",
    )
    rule: Mapped["Rule"] = relationship(
        "Rule",
        back_populates="hotel",
    )
