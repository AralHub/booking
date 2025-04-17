from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship
from app.models import Base
from app.models.mixins import IntIdPkMixin, MultilingualNameMixin

if TYPE_CHECKING:
    from app.models.booking import Booking


class PaymentMethod(
    IntIdPkMixin,
    MultilingualNameMixin,
    Base,
):
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="payment_method",
    )
