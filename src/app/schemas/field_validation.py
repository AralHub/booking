from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field

from app.models.booking import BookingStatus
from app.models.user import GENDER_TYPES

# Константы
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 30
HOTEL_NAME_MAX_LENGTH = 255
URL_PATTERN = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
TIME_PATTERN = r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$"
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


# Общие поля с аннотациями
NAME_FIELD = Annotated[
    str,
    Field(
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
        examples=["User Userson"],
    ),
]
NAME_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
        examples=["User Userberg"],
        default=None,
    ),
]
PASSWORD_FIELD = Annotated[
    str,
    Field(
        pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
        examples=["pass123"],
    ),
]

PHONE_NUMBER_FIELD = Annotated[
    str, Field(pattern=r"^[1-9]\d{1,14}$", examples=["998991234567"])
]

PHONE_NUMBER_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        pattern=r"^[1-9]\d{1,14}$",
        examples=["998991112233"],
        default=None,
    ),
]

BIRTHDAY_FIELD = Annotated[
    datetime | None,
    Field(
        examples=["1990-01-01"],
        default=None,
    ),
]
GENDER_FIELD = Annotated[
    GENDER_TYPES,
    Field(
        examples=["male", "female"],
        default=GENDER_TYPES.MALE.value,
    ),
]

VERIFY_CODE_FIELD = Annotated[
    str,
    Field(pattern=r"^\d{5}$", examples=["12345"]),
]

LONG_FIELD = Annotated[
    float | None,
    Field(
        ge=-180,
        le=180,
        default=None,
    ),
]
LAT_FIELD = Annotated[
    float | None,
    Field(
        ge=-90,
        le=90,
        default=None,
    ),
]

DATE_FIELD = Annotated[
    str,
    Field(
        pattern=DATE_PATTERN,
        examples=["2025-03-12"],
        description="Date in YYYY-MM-DD format",
    ),
]
HOTEL_NAME_FIELD = Annotated[
    str,
    Field(
        min_length=MIN_NAME_LENGTH,
        max_length=HOTEL_NAME_MAX_LENGTH,
        examples=["Hotel1"],
    ),
]
HOTEL_NAME_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        min_length=MIN_NAME_LENGTH,
        max_length=HOTEL_NAME_MAX_LENGTH,
        examples=["Hotel2"],
        default=None,
    ),
]
EMAIL_FIELD = Annotated[
    EmailStr,
    Field(
        examples=["example@example.com"],
    ),
]
EMAIL_FIELD_UPDATE = Annotated[
    EmailStr | None,
    Field(
        examples=["example@example.com"],
        default=None,
    ),
]
SITE_URL_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        pattern=URL_PATTERN,
        examples=["https://www.burger-king.com"],
        default=None,
    ),
]
TIME_FIELD = Annotated[
    str,
    Field(
        pattern=TIME_PATTERN,
        examples=["14:30"],
        description="Time in 24-hour format (HH:MM)",
    ),
]
TIME_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        pattern=TIME_PATTERN,
        examples=["14:30"],
        description="Time in 24-hour format (HH:MM)",
        default=None,
    ),
]
BOOKING_STATUS_FIELD = Annotated[
    BookingStatus,
    Field(
        examples=[BookingStatus.CANCELLED.value],
        default=BookingStatus.PENDING,
    ),
]
BOOKING_STATUS_FIELD_UPDATE = Annotated[
    BookingStatus | None,
    Field(
        examples=[BookingStatus.CANCELLED.value],
        default=None,
    ),
]
