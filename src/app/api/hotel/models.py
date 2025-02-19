from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from ..locations.models import City, Coordinate
    from ..review.models import Review  # noqa
    from .amenity.models import Amenity, HotelAmenityAssociation
    from .room.models import Room


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
    address: Mapped[str] = mapped_column(String(255), nullable=True)
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
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    city: Mapped["City"] = relationship("City", back_populates="hotels")
    hotel_category_id: Mapped[int] = mapped_column(
        ForeignKey("hotel_categories.id"),
    )
    hotel_category: Mapped["HotelCategory"] = relationship(
        "HotelCategory",
        back_populates="hotels",
    )
    amenity_association: Mapped[list["HotelAmenityAssociation"]] = relationship(
        "HotelAmenityAssociation",
        back_populates="hotel",
    )
    amenities: Mapped[list["Amenity"]] = relationship(
        secondary="hotel_amenity_association",
        back_populates="hotels",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="hotel",
    )
    coordinate_id: Mapped[int] = mapped_column(ForeignKey("coordinates.id"))
    coordinate: Mapped["Coordinate"] = relationship(
        "Coordinate",
        uselist=False,
        single_parent=True,
    )
