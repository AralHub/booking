from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from app.api.user.schemas import PHONE_NUMBER_FIELD, PHONE_NUMBER_FIELD_UPDATE

NAME_MAX_LENGTH = 255
NAME_MIN_LENGTH = 3
URL_PATTERN = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
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

# region Hotel Full


class BookingInformation(BaseModel):
    check_in: str  # Format: "HH:MM"
    check_out: str  # Format: "HH:MM"
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


class HotelFullUpdate(BaseModel):
    pass


class HotelFullUpdateInternal(HotelFullUpdate):
    pass


# endregion


# region Hotel Name
class HotelNameBase(BaseModel):
    name: NAME_FIELD
    description: str
    slug: str


class HotelNameRead(HotelNameBase):
    id: int
    hotel_category_id: int


class HotelNameCreate(BaseModel):
    name: NAME_FIELD
    description: str | None = None
    hotel_category_id: int


class HotelNameCreateInternal(HotelNameCreate):
    slug: str
    hotel_admin_id: int
    is_active: bool = False
    created_at: datetime


class HotelNameUpdate(BaseModel):
    name: NAME_FIELD_UPDATE = None
    description: str | None = None
    slug: str | None = None
    hotel_category_id: int | None = None


class HotelNameFilter(BaseModel):
    id: int | None = None
    name: NAME_FIELD_UPDATE = None
    slug: str | None = None
    hotel_category_id: int | None = None


# endregion
# region HotelInfo


class HotelInfoBase(BaseModel):
    first_phone_number: PHONE_NUMBER_FIELD
    email: EMAIL_FIELD


class HotelInfoRead(HotelInfoBase):
    id: int
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE
    hotel_id: int


class HotelInfoCreate(HotelInfoBase):
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE


class HotelInfoCreateInternal(HotelInfoCreate):
    hotel_id: int


class HotelInfoUpdate(BaseModel):
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE
    email: EMAIL_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE


class HotelInfoUpdateInternal(HotelInfoUpdate):
    hotel_id: int


class HotelInfoFilter(BaseModel):
    id: int | None = None
    first_phone_number: str | None = None
    second_phone_number: str | None = None
    email: EMAIL_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE
    hotel_id: int | None = None


# endregion


# region Hotel Category
class HotelCategoryBase(BaseModel):
    name: str


class HotelCategoryRead(HotelCategoryBase):
    id: int


class HotelCategoryCreate(HotelCategoryBase):
    pass


class HotelCategoryCreateInternal(HotelCategoryCreate):
    pass


class HotelCategoryUpdate(BaseModel):
    name: str | None = None


class HotelCategoryUpdateInternal(HotelCategoryUpdate):
    pass


class HotelCategoryFilter(BaseModel):
    id: int | None = None
    name: str | None = None


# endregion
