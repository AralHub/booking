from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
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
    locations: Mapped[list["Location"]] = relationship(
        "Location",
        back_populates="country",
        cascade="all, delete-orphan",
    )


class City(IntIdPkMixin, Base):
    __tablename__ = "cities"
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    # relationships
    country_id: Mapped[int] = mapped_column(
        ForeignKey(
            "countries.id",
            ondelete="CASCADE",
        )
    )
    country: Mapped["Country"] = relationship(
        "Country",
        back_populates="cities",
    )
    locations: Mapped[list["Location"]] = relationship(
        "Location",
        back_populates="city",
        cascade="all, delete-orphan",
    )


class Location(IntIdPkMixin, Base):
    __tablename__ = "locations"
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    hotel: Mapped["Hotel"] = relationship(back_populates="location")
    country: Mapped["Country"] = relationship(back_populates="locations")
    city: Mapped["City"] = relationship(back_populates="locations")
