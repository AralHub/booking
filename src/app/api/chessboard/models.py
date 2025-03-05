from datetime import date
from app.core import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Boolean,
    UniqueConstraint,
)
from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin
from typing import TYPE_CHECKING

from src.app.api.booking.models import Booking

if TYPE_CHECKING:
    from app.api.room.models import Room


class RoomDateAvailability(IntIdPkMixin, Base):
    __tablename__ = "room_date_availabilities"

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    check_date: Mapped[date] = mapped_column(Date, nullable=False)
    available_quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="date_availabilities")

    __table_args__ = (
        UniqueConstraint("room_id", "date", name="unique_room_date_availability"),
    )
