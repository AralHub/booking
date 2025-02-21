from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    ...


class PaymentType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))


class Payment(IntIdPkMixin, Base):
    pass
