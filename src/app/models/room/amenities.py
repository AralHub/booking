from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.room import Room


class RoomAmenityCategory(IntIdPkMixin, Base):
    __tablename__ = "room_amenity_categories"
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    room_amenities: Mapped[list["RoomAmenity"]] = relationship(
        back_populates="room_amenity_category",
    )


class RoomAmenity(IntIdPkMixin, Base):
    __tablename__ = "room_amenities"
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    icon: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        server_default=None,
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
