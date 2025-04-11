from pydantic import BaseModel, ConfigDict

from ..mixins import (
    MultilingualDescriptionBase,
    MultilingualDescriptionBaseUpdate,
    MultilingualNameBase,
    MultilingualNameBaseUpdate,
)


class HotelCategoryBase(MultilingualNameBase):
    pass


class HotelCategoryRead(BaseModel):
    id: int
    name: dict[str, str]
    description: dict[str, str]
    model_config = ConfigDict(from_attributes=True)


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
