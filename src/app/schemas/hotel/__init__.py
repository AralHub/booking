from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import PHONE_NUMBER_FIELD, PHONE_NUMBER_FIELD_UPDATE

NAME_MAX_LENGTH = 255
NAME_MIN_LENGTH = 3
URL_PATTERN = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
TIME_PATTERN = r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$"
# DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
# DATE_FIELD = Annotated[
#     str,
#     Field(
#         pattern=DATE_PATTERN,
#         examples=["2025-03-12"],
#         description="Date in YYYY-MM-DD format",
#     ),
# ]
NAME_FIELD = Annotated[
    str,
    Field(
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
        examples=["Hotel1"],
    ),
]
NAME_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
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


class BookingInformation(BaseModel):
    check_in: TIME_FIELD
    check_out: TIME_FIELD
    star_rating: int | None = None


class GuestInformation(BaseModel):
    email_for_guests: EMAIL_FIELD
    first_phone_for_guests: PHONE_NUMBER_FIELD
    second_phone_for_guests: PHONE_NUMBER_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE


class HotelFullCreate(BaseModel):
    name: NAME_FIELD
    hotel_category_id: int = 1
    description: str | None = None
    address: str
    city_id: int
    latitude: float
    longitude: float
    facilities: list[int]
    information_for_booking: BookingInformation
    information_for_guests: GuestInformation


class HotelFullCreateInternal(HotelFullCreate):
    hotel_admin_id: int
    created_at: datetime
    slug: str | None = None


class BookingInformationUpdate(BaseModel):
    check_in: TIME_FIELD_UPDATE
    check_out: TIME_FIELD_UPDATE
    star_rating: int | None = None


class GuestInformationUpdate(BaseModel):
    email_for_guests: EMAIL_FIELD_UPDATE
    first_phone_for_guests: PHONE_NUMBER_FIELD_UPDATE
    second_phone_for_guests: PHONE_NUMBER_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE


class HotelFullUpdate(BaseModel):
    name: NAME_FIELD_UPDATE
    hotel_category_id: int | None = None
    description: str | None = None
    address: str | None = None
    city_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    facilities: list[int] | None = None
    information_for_booking: BookingInformationUpdate
    information_for_guests: GuestInformationUpdate


class HotelFullUpdateInternal(HotelFullUpdate):
    hotel_id: int


# class BookingInformationRead(BaseModel):
#     check_in: TIME_FIELD
#     check_out: TIME_FIELD
#     star_rating: int | None = None


# class GuestInformationRead(BaseModel):
#     email_for_guests: EMAIL_FIELD_UPDATE
#     first_phone_for_guests: PHONE_NUMBER_FIELD
#     second_phone_for_guests: PHONE_NUMBER_FIELD_UPDATE
#     site_url: str | None = None


# class HotelFullRead(BaseModel):
#     id: int
#     name: str
#     hotel_category_id: int
#     description: str | None = None
#     address: str
#     city_id: int
#     latitude: float
#     longitude: float
#     facilities: list[int]
#     information_for_booking: BookingInformationRead
#     information_for_guests: GuestInformationRead
#     created_at: datetime
#     updated_at: datetime | None = None
#     slug: str | None = None

#     class Config:
#         from_attributes = True


class HotelSearch(BaseModel):
    city_id: int
    check_in: date
    check_out: date
    guests: list[int]
