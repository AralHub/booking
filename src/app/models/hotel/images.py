from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class HotelImage(IntIdPkMixin, Base):
    image: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(back_populates="hotel_images")
