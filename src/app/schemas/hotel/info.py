from datetime import datetime

from pydantic import BaseModel

from app.schemas.field_validation import (
    EMAIL_FIELD,
    EMAIL_FIELD_UPDATE,
    HOTEL_NAME_FIELD,
    HOTEL_NAME_FIELD_UPDATE,
    SITE_URL_FIELD_UPDATE,
)
from app.schemas.user import PHONE_NUMBER_FIELD, PHONE_NUMBER_FIELD_UPDATE


# region Hotel Name
class HotelNameBase(BaseModel):
    name: HOTEL_NAME_FIELD
    description: str
    slug: str


class HotelNameRead(HotelNameBase):
    id: int
    hotel_category_id: int


class HotelNameCreate(BaseModel):
    name: dict[str, str]
    description: dict[str, str]
    hotel_category_id: int


class HotelNameCreateInternal(HotelNameCreate):
    slug: str
    hotel_admin_id: int
    is_active: bool = False
    created_at: datetime


class HotelNameUpdate(BaseModel):
    name: HOTEL_NAME_FIELD_UPDATE = None
    description: str | None = None
    slug: str | None = None
    hotel_category_id: int | None = None


class HotelNameUpdateInternal(HotelNameUpdate):
    id: int


class HotelNameFilter(BaseModel):
    id: int | None = None
    name: HOTEL_NAME_FIELD_UPDATE = None
    description: str | None = None
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


class HotelInfoNameRead(HotelInfoRead):
    hotel_name: str
    hotel_description: str
    hotel_slug: str
    hotel_category_id: int


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
    hotel_id: int | None = None
    first_phone_number: str | None = None
    second_phone_number: str | None = None
    email: EMAIL_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE


# endregion
