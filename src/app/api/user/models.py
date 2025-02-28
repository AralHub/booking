from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Date, ForeignKey, String, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.api.booking.models import Booking
    from app.api.hotel_admin.models import HotelAdmin
    from app.api.review.models import Review


class GENDER_TYPES(str, Enum):
    MALE = "male"
    FEMALE = "female"


class User(IntIdPkMixin, TimestampMixin, SoftDeleteMixin, Base):
    phone_number: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        default=None,
        server_default=None,
    )
    password: Mapped[str] = mapped_column(
        String,
        nullable=True,
        default=None,
        server_default=None,
    )
    first_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    birthday: Mapped[datetime] = mapped_column(
        Date,
        nullable=True,
    )
    gender: Mapped[GENDER_TYPES] = mapped_column(
        SqlEnum(GENDER_TYPES, name="gender_types"),
        default=GENDER_TYPES.MALE,
        server_default=text("'MALE'"),
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

    # relationships
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="user",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
    )
    hotel_admin: Mapped["HotelAdmin"] = relationship(
        "HotelAdmin",
        back_populates="user",
    )
    role: Mapped["UserRole"] = relationship(
        "UserRole",
        back_populates="user",
    )


class UserRole(IntIdPkMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="role")


class TokenBlacklist(IntIdPkMixin, Base):
    jti: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
    )
    is_blacklisted: Mapped[bool] = mapped_column(
        default=True,
        server_default="true",
    )
