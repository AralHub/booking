from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models import Hotel


class Rule(IntIdPkMixin, Base):
    # Check-in time range
    check_in_from: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
        default="12:00",
    )
    check_in_until: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
        default="00:00",
    )

    # Check-out time range
    check_out_from: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
        default="12:00",
    )
    check_out_until: Mapped[Time] = mapped_column(
        Time,
        nullable=True,
    )
    is_pet_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="rule",
    )
