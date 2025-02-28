from typing import Annotated

from pydantic import BaseModel, Field

PHONE_NUMBER_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        pattern=r"^\+?[1-9]\d{1,14}$",
        examples=["+998991112233"],
        default=None,
    ),
]


class HotelAdminInfoBase(BaseModel):
    name: str


class HotelAdminInfoRead(HotelAdminInfoBase):
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None


class HotelAdminInfoCreate(HotelAdminInfoBase):
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None


class HotelAdminInfoCreateInternal(HotelAdminInfoCreate):
    hotel_id: int


class HotelAdminInfoUpdate(BaseModel):
    name: str | None = None
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None


class HotelAdminInfoUpdateInternal(HotelAdminInfoUpdate):
    hotel_id: int


class HotelAdminInfoFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    first_phone_number: str | None = None
    second_phone_number: str | None = None
    hotel_id: int | None = None
