from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from ..country.models import City
    from .room.models import Room


class HotelCategory(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(30))
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel",
        back_populates="hotel_category",
    )


class Hotel(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(30))
    domain: Mapped[str] = mapped_column(String(30), unique=True)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    preview_photo_path: Mapped[str] = mapped_column(String, nullable=True)
    # rooms_quantity: Mapped[int] = mapped_column(Integer, default=0)
    # relationships
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # amenities: Mapped[list["Amenity"]] = relationship(
    #     "Amenity",
    #     back_populates="hotels",
    #     cascade="all, delete-orphan",
    # )
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="hotel",
        cascade="all, delete-orphan",
    )
    city_id: Mapped[int] = mapped_column(ForeignKey("citys.id"))
    city: Mapped["City"] = relationship("City", back_populates="hotels")
    hotel_category_id: Mapped[int] = mapped_column(
        ForeignKey("hotel_categorys.id"),
    )
    hotel_category: Mapped["HotelCategory"] = relationship(
        "HotelCategory",
        back_populates="hotels",
    )
