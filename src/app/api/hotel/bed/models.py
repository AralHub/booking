from typing import TYPE_CHECKING

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    pass


class BedType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    max_capacity: Mapped[int] = mapped_column()


class Bed(IntIdPkMixin, Base):
    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=5,
        server_default="5",
    )
    preview_photo_path: Mapped[str] = mapped_column(String, nullable=True)

    # relationships
