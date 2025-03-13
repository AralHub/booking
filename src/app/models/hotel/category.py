from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class HotelCategory(IntIdPkMixin, Base):
    __tablename__ = "hotel_categories"
    name: Mapped[str] = mapped_column(String, unique=True)
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel",
        back_populates="hotel_category",
    )
