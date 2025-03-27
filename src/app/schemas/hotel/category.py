from pydantic import BaseModel

from ..mixins import (
    MultilingualDescriptionBase,
    MultilingualDescriptionBaseUpdate,
    MultilingualNameBase,
    MultilingualNameBaseUpdate,
)


class HotelCategoryBase(MultilingualNameBase):
    pass


class HotelCategoryRead(HotelCategoryBase):
    id: int


class HotelCategoryCreate(
    HotelCategoryBase,
    MultilingualDescriptionBase,
):
    pass


class HotelCategoryCreateInternal(BaseModel):
    name: dict[str, str]
    description: dict[str, str]


class HotelCategoryUpdate(
    MultilingualNameBaseUpdate,
    MultilingualDescriptionBaseUpdate,
):
    pass


class HotelCategoryUpdateInternal(BaseModel):
    name: dict[str, str]
    description: dict[str, str]


class HotelCategoryFilter(BaseModel):
    id: int | None = None
