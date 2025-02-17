from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models.room import Room
    from app.api.user.models import User


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
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    # relationships
    city_id: Mapped[int] = mapped_column(ForeignKey("citys.id"))

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["Room"] = relationship("Rooms", back_populates="booking")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("Users", back_populates="booking")
