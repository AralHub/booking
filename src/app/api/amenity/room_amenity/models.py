from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.room.models import Room


class RoomAmenityCategory(IntIdPkMixin, Base):
    __tablename__ = "room_amenity_categories"
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    room_amenities: Mapped[list["RoomAmenity"]] = relationship(
        back_populates="room_amenity_category",
    )


class RoomAmenity(IntIdPkMixin, Base):
    __tablename__ = "room_amenities"
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    room_amenity_category_id: Mapped[int] = mapped_column(
        ForeignKey("room_amenity_categories.id"),
    )
    room_amenity_category: Mapped[RoomAmenityCategory] = relationship(
        back_populates="room_amenities",
    )
    room_association: Mapped[list["RoomAmenityAssociation"]] = relationship(
        "RoomAmenityAssociation",
        back_populates="room_amenity",
        cascade="all, delete-orphan",
    )
    rooms: Mapped[list["Room"]] = relationship(
        secondary="room_amenity_associations",
        back_populates="room_amenities",
    )


class RoomAmenityAssociation(Base):
    __tablename__ = "room_amenity_associations"
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"),
        primary_key=True,
    )
    room_amenity_id: Mapped[int] = mapped_column(
        ForeignKey("room_amenities.id"),
        primary_key=True,
    )
    # association between Assocation -> Room
    room: Mapped["Room"] = relationship(
        "Room",
        back_populates="room_amenity_association",
    )
    # association between Assocation -> Amenity
    room_amenity: Mapped[RoomAmenity] = relationship(
        "RoomAmenity",
        back_populates="room_association",
    )
    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "room_amenity_id",
            name="uq_room_amenity",
        ),
    )
