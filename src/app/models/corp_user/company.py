from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.corp_user import CorpUser


class Company(
    IntIdPkMixin,
    TimestampMixin,
    Base,
):
    company_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    inn: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    bank_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id"),
        nullable=False,
    )
    corp_user_id: Mapped[int] = mapped_column(
        ForeignKey("corp_users.id"),
        nullable=False,
    )
    corp_user: Mapped["CorpUser"] = relationship(
        "CorpUser",
        back_populates="company",
    )
