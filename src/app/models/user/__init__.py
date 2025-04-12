from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, String, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.company import Company
    from app.models.favorites import UserFavorite
    from app.models.review import Review


class GENDER_TYPES(str, Enum):
    MALE = "male"
    FEMALE = "female"


from app.models.booking import BookingType


class User(IntIdPkMixin, TimestampMixin, SoftDeleteMixin, Base):
    phone_number: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    birthday: Mapped[date] = mapped_column(
        Date,
        nullable=True,
    )
    gender: Mapped[GENDER_TYPES] = mapped_column(
        SqlEnum(GENDER_TYPES, name="gender_types"),
        nullable=True,
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
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    role: Mapped[BookingType] = mapped_column(
        SqlEnum(BookingType),
        nullable=False,
        default=BookingType.PERSONAL,
        server_default=text("'PERSONAL'"),
    )
    # relationships
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id"),
        nullable=True,
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
    company: Mapped[Optional["Company"]] = relationship(
        "Company",
        back_populates="user",
        uselist=False,
    )
