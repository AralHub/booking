from pydantic import BaseModel, ConfigDict

from app.schemas.mixins import (
    MultilingualNameBase,
    MultilingualNameBaseUpdate,
)

# region HotelAmenityCategory


class HotelAmenityCategoryCreate(MultilingualNameBase):
    pass


class HotelAmenityCategoryCreateInternal(BaseModel):
    name: dict[str, str]


class HotelAmenityCategoryUpdate(MultilingualNameBaseUpdate):
    pass


class HotelAmenityCategoryFilter(BaseModel):
    id: int | None = None


class HotelAmenityCategoryRead(BaseModel):
    id: int
    name: dict[str, str]


# endregion

# region HotelAmenity


class HotelAmenityCreate(MultilingualNameBase):
    is_popular: bool | None = None


class HotelAmenityCreateInternal(BaseModel):
    name: dict[str, str]
    hotel_amenity_category_id: int


class HotelAmenityRead(BaseModel):
    id: int
    name: dict[str, str]
    icon: str | None = None
    hotel_amenity_category_id: int
    model_config = ConfigDict(from_attributes=True)


class HotelAmenityUpdate(MultilingualNameBaseUpdate):
    is_popular: bool | None = None


class HotelAmenityUpdateInternal(BaseModel):
    name: dict[str, str]


class HotelAmenityFilter(BaseModel):
    id: int | None = None
    hotel_amenity_category_id: int | None = None


# endregion


class HotelAmenityCategoryWithAmenities(BaseModel):
    id: int
    name: dict[str, str]
    hotel_amenities: list[HotelAmenityRead]
