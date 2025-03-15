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
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.room.types import RoomType


class ChessBoard(IntIdPkMixin, Base):
    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))
    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")
    check_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    available_rooms_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_closed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "date",
            name="unique_room_date_availability",
        ),
    )
