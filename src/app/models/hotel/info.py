from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class HotelInfo(IntIdPkMixin, Base):
    first_phone_number: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    second_phone_number: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        server_default=None,
    )
    site_url: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(back_populates="hotel_info")
