from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.models import Base
from app.models.mixins import (
    IntIdPkMixin,
    MultilingualDescriptionMixin,
    MultilingualNameMixin,
)

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class HotelCategory(
    IntIdPkMixin,
    MultilingualDescriptionMixin,
    MultilingualNameMixin,
    Base,
):
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel",
        back_populates="hotel_category",
    )
