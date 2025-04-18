from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.room import Room


class ChessBoard(IntIdPkMixin, Base):
    check_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    available_rooms_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(back_populates="chessboards")
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["Room"] = relationship(back_populates="chessboards")
    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "hotel_id",
            "check_date",
        ),
    )
