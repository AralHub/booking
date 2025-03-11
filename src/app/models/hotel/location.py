from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.location import City


class HotelLocation(IntIdPkMixin, Base):
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    to_airport: Mapped[float] = mapped_column(Float, nullable=True)
    to_railway: Mapped[float] = mapped_column(Float, nullable=True)
    to_city_center: Mapped[float] = mapped_column(Float, nullable=True)
    # relationships
    hotel: Mapped["Hotel"] = relationship(back_populates="location")
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    city: Mapped["City"] = relationship(
        "City",
        back_populates="locations",
    )
