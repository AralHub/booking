from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.user import User


class UserFavorite(IntIdPkMixin, Base):
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship("Hotel")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="favorites")

    __table_args__ = (UniqueConstraint("user_id", "hotel_id", name="unique_user_hotel"),)
