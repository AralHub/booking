from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models import Hotel


class HotelAdmin(IntIdPkMixin, Base):
    phone_number: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        default=None,
        server_default=None,
    )
    password: Mapped[str] = mapped_column(
        String,
        nullable=True,
        default=None,
        server_default=None,
    )
    first_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(back_populates="hotel_admin")
