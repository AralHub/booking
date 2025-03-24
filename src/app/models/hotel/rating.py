from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class HotelRating(IntIdPkMixin, Base):
    average_rating: Mapped[float] = mapped_column(Float)
    reviews_count: Mapped[int] = mapped_column(Integer)
    # relationships
    hotel: Mapped["Hotel"] = relationship(back_populates="location")
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
