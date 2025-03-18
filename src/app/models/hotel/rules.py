from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class HotelRule(IntIdPkMixin, Base):
    # Check-in time range
    check_in_from: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="12:00",
    )
    check_in_until: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    # Check-out time range
    check_out_from: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="12:00",
    )
    check_out_until: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="rule",
    )
