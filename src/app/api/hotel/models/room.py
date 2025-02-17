from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .hotel import Hotel
    from app.api.booking.models import Booking
    

class RoomType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(30))
    max_capacity: Mapped[int] = mapped_column()

    # relationships
    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")


class Room(IntIdPkMixin, Base):
    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=5,
        server_default="5",
    )
    preview_photo_path: Mapped[str] = mapped_column(String, nullable=True)

    # relationships
    hotel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "hotels.id",
            ondelete="CASCADE",
        ),
    )
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="rooms",
    )
    room_type_id: Mapped["RoomType"] = mapped_column(ForeignKey("room_types.id"))
    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")

    booking: Mapped["Booking"] = relationship(back_populates="room")
