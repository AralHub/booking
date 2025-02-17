from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Computed, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from ..auth.models import User
    from ..hotel.models.room import Room


class Booking(IntIdPkMixin, Base):

    start_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
    )
    end_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
    )
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cost: Mapped[int] = mapped_column(
        Integer, Computed("(start_date - end_date) * price")
    )
    total_days: Mapped[int] = mapped_column(Integer, Computed("(date_to - date_from)"))

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("Users", back_populates="booking")
    room: Mapped["Room"] = relationship("Rooms", back_populates="booking")
