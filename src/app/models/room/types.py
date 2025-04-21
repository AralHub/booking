from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.models import Base
from app.models.mixins import (
    IntIdPkMixin,
    MultilingualNameMixin,
)

if TYPE_CHECKING:
    from app.models.room import Room


class RoomType(IntIdPkMixin, MultilingualNameMixin, Base):
    # relationships
    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")
