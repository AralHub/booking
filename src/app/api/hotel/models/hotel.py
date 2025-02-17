from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .room import Room  # noqa: F401


class Hotel(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(30))
    domain: Mapped[str] = mapped_column(String(30), unique=True)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    preview_photo_path: Mapped[str] = mapped_column(String, nullable=True)

    # relationships
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="hotel",
        cascade="all, delete-orphan",
    )
