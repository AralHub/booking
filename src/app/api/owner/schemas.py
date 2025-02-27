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


class HotelOwnerInfoBase(BaseModel):
    name: str


class HotelOwnerInfoRead(HotelOwnerInfoBase):
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None


class HotelOwnerInfoCreate(HotelOwnerInfoBase):
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None


class HotelOwnerInfoCreateInternal(HotelOwnerInfoCreate):
    hotel_id: int


class HotelOwnerInfoUpdate(BaseModel):
    name: str | None = None
    first_phone_number: PHONE_NUMBER_FIELD_UPDATE = None
    second_phone_number: PHONE_NUMBER_FIELD_UPDATE = None


class HotelOwnerInfoUpdateInternal(HotelOwnerInfoUpdate):
    pass


class HotelOwnerInfoFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    first_phone_number: str | None = None
    second_phone_number: str | None = None
    hotel_id: int | None = None
