from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

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
class HotelBase(BaseModel):
    name: NAME_FIELD
    description: str
    slug: str


class HotelRead(HotelBase):
    id: int
    hotel_category_id: int


class HotelCreate(HotelBase):
    slug: str
    hotel_category_id: int


class HotelCreateInternal(HotelCreate):
    hotel_admin_id: int
    created_at: datetime


class HotelUpdate(BaseModel):
    name: NAME_FIELD_UPDATE = None
    description: str | None = None
    slug: str | None = None


class HotelUpdateInternal(HotelUpdate):
    image: str | None = None


class HotelFilter(BaseModel):
    id: int | None = None
    name: NAME_FIELD_UPDATE = None
    slug: str | None = None
    hotel_category_id: int | None = None


class HotelSearch(BaseModel):
    rating: float | None = None
    amenities: list[int] | None = None
    city_id: int | None = None
    to_city_center: float | None = None
    total_cost: float | None = None


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
