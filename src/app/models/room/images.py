from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.room import Room


class RoomImage(IntIdPkMixin, Base):
    image: Mapped[str] = mapped_column(String, nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["Room"] = relationship(back_populates="room_images")
