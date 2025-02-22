from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from ..images.models import Image

    # from ..language.models import Language
    from ..locations.models import Location
    from ..review.models import Review  # noqa
    from .amenity.models import HotelAmenity, HotelAmenityAssociation
    from .room.models import Room


# class Rules(IntIdPkMixin, Base):
#     name: Mapped[str] = mapped_column(String(255))


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
    preview_photo_path: Mapped[str] = mapped_column(String, nullable=True)
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
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
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
