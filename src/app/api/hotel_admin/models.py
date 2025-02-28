from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models import Hotel
    from app.api.user.models import User


class HotelAdmin(IntIdPkMixin, Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="hotel_admin")
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(back_populates="hotel_admin")


class HotelAdminInfo(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(
        String(30),
        unique=True,
    )
    first_phone_number: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    second_phone_number: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel = relationship("Hotel", back_populates="hotel_admin_info")
