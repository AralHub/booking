from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models.hotel import Hotel


class Country(IntIdPkMixin, Base):
    __tablename__ = "countries"
    name: Mapped[str] = mapped_column(
        String(30),
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
        String(30),
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
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel",
        back_populates="city",
        cascade="all, delete-orphan",
    )


class Coordinate(IntIdPkMixin, Base):
    __tablename__ = "coordinates"
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
