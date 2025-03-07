from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.room.models import RoomTypeVariant


class RoomAvailability(IntIdPkMixin, Base):
    __tablename__ = "room_availabilities"

    room_type_variant_id: Mapped[int] = mapped_column(
        ForeignKey("room_type_variants.id")
    )
    room_type_variant: Mapped["RoomTypeVariant"] = relationship(back_populates="rooms")
    check_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    available_rooms: Mapped[int] = mapped_column(Integer, nullable=False)
    is_closed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    __table_args__ = (
        UniqueConstraint("room_id", "date", name="unique_room_date_availability"),
    )
