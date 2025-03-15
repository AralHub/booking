from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.room import Room


class RoomPrice(IntIdPkMixin, Base):
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    guest_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    room: Mapped["Room"] = relationship(back_populates="room_prices")
