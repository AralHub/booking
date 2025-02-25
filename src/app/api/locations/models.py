from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from ..hotel.models import Hotel


class Country(IntIdPkMixin, Base):
    __tablename__ = "countries"
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )
    code: Mapped[str] = mapped_column(
        String(30),
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
        String(255),
        unique=True,
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    properties_count: Mapped[int] = mapped_column(Integer)
    aero_lat: Mapped[float] = mapped_column(Float)
    aero_lng: Mapped[float] = mapped_column(Float)
    rail_lat: Mapped[float] = mapped_column(Float)
    rail_lng: Mapped[float] = mapped_column(Float)
    image: Mapped[str] = mapped_column(String(255))
    # relationships
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    country: Mapped["Country"] = relationship(
        "Country",
        back_populates="cities",
    )
    locations: Mapped[list["Location"]] = relationship(
        "Location",
        back_populates="city",
    )


class Location(IntIdPkMixin, Base):
    __tablename__ = "locations"
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    geocode_lat: Mapped[float] = mapped_column(Float)
    geocode_lng: Mapped[float] = mapped_column(Float)

    # relationships
    hotel: Mapped["Hotel"] = relationship(back_populates="location")
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    city: Mapped["City"] = relationship(
        "City",
        back_populates="locations",
    )
