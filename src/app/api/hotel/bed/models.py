from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    pass


class BedType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    max_capacity: Mapped[int] = mapped_column()
