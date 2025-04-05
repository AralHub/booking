from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.corp_user.company import Company
    from app.models.favorites import UserFavorite
    from app.models.review import Review


class CorpUser(
    IntIdPkMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    phone_number: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    position: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    is_fully_registered: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    is_active: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )

    # relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="corp_user",
    )

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="user",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
    )
    favorites: Mapped[list["UserFavorite"]] = relationship(
        "UserFavorite",
        back_populates="user",
    )
