from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from ..hotel.models import Hotel
    from ..room.models import Room


class HotelImage(IntIdPkMixin, Base):
    image: Mapped[str] = mapped_column(String, nullable=False)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(back_populates="hotel_images")


class RoomImage(IntIdPkMixin, Base):
    image: Mapped[str] = mapped_column(String, nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["Room"] = relationship(back_populates="room_images")
