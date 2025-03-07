from datetime import datetime
from typing import Annotated

from pydantic import AnyUrl, BaseModel, Field

NAME_MAX_LENGTH = 255
NAME_MIN_LENGTH = 3
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


# region Hotel


class BookingInformation(BaseModel):
    check_in: str  # Format: "HH:MM"
    check_out: str  # Format: "HH:MM"
    star_rating: int | None = None


class GuestInformation(BaseModel):
    email_for_guests: str
    first_phone_for_guests: str
    second_phone_for_guests: str | None = None
    site_url: AnyUrl | None = None


class HotelFullCreate(BaseModel):
    name: NAME_FIELD
    hotel_category_id: int
    description: str | None = None
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
    slug: str
    hotel_category_id: int


class HotelNameCreateInternal(HotelNameCreate):
    hotel_admin_id: int
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

# region HotelInfo

PHONE_NUMBER_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        pattern=r"^\+?[1-9]\d{1,14}$",
        examples=["+998991112233"],
        default=None,
    ),
]


class HotelInfoBase(BaseModel):
    name: str


class HotelInfoRead(HotelInfoBase):
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    email: str | None = None
    site_url: AnyUrl | None = None


class HotelInfoCreate(HotelInfoBase):
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    email: str | None = None
    site_url: AnyUrl | None = None


class HotelInfoCreateInternal(HotelInfoCreate):
    hotel_id: int


class HotelInfoUpdate(BaseModel):
    name: str | None = None
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    email: str | None = None
    site_url: AnyUrl | None = None


class HotelInfoUpdateInternal(HotelInfoUpdate):
    hotel_id: int


class HotelInfoFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    first_phone_number: str | None = None
    second_phone_number: str | None = None
    email: str | None = None
    site_url: AnyUrl | None = None
    hotel_id: int | None = None


# endregion
