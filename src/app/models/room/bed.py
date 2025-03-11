from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.room import Room


class BedType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    room_bed_configs: Mapped[list["RoomBedConfiguration"]] = relationship(
        back_populates="bed_type"
    )


class RoomBedConfiguration(IntIdPkMixin, Base):
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    bed_type_id: Mapped[int] = mapped_column(ForeignKey("bed_types.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    # relationships
    room: Mapped["Room"] = relationship(back_populates="bed_configurations")
    bed_type: Mapped["BedType"] = relationship(back_populates="room_bed_configs")
