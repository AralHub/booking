from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.room import Room


class RoomType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    # relationships
    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")
