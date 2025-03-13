from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel.location import HotelLocation


class Country(IntIdPkMixin, Base):
    __tablename__ = "countries"
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
    )
    code: Mapped[str] = mapped_column(
        String,
        unique=True,
    )

    # relationships
    cities: Mapped[list["City"]] = relationship(
        "City",
        back_populates="country",
        cascade="all, delete-orphan",
    )


class City(IntIdPkMixin, Base):
    __tablename__ = "cities"
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    properties_count: Mapped[int] = mapped_column(Integer)
    geocode_lng: Mapped[float] = mapped_column(Float)
    geocode_lat: Mapped[float] = mapped_column(Float)
    aero_lat: Mapped[float] = mapped_column(Float)
    aero_lng: Mapped[float] = mapped_column(Float)
    rail_lat: Mapped[float] = mapped_column(Float)
    rail_lng: Mapped[float] = mapped_column(Float)

    image: Mapped[str] = mapped_column(String)
    # relationships
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    country: Mapped["Country"] = relationship(
        "Country",
        back_populates="cities",
    )
    locations: Mapped[list["HotelLocation"]] = relationship(
        "HotelLocation",
        back_populates="city",
    )
