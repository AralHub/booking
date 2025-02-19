from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models import Room
    from app.api.user.models import User


class Booking(IntIdPkMixin, Base):
    check_in_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
    )
    check_out_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    # relationships
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["Room"] = relationship("Room", back_populates="booking")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    __table_args__ = (
        CheckConstraint(
            "check_in_date < check_out_date",
            name="check_in_date_before_check_out_date",
        ),
    )
