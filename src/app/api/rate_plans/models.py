from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.api.hotel.models import Hotel


class RatePlan(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )
