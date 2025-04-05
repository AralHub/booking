from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.mixins import IntIdPkMixin

# if TYPE_CHECKING:
    # from app.models.room.types import RoomType


class ChessBoard(IntIdPkMixin, Base):
    check_date: Mapped[date] = mapped_column(Date, nullable=False)
    available_rooms_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_closed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    # room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))
    # room_type: Mapped["RoomType"] = relationship(back_populates="rooms")
