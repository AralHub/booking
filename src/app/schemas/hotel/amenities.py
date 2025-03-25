from pydantic import BaseModel

from app.models.hotel.amenities import PaymentType
from app.schemas.mixins import (
    MultilingualNameBase,
    MultilingualNameBaseUpdate,
)

# region HotelAmenity


class HotelAmenityCreate(MultilingualNameBase):
    is_popular: bool
    payment_type: PaymentType


class HotelAmenityCreateInternal(BaseModel):
    name: dict[str, str]
    hotel_amenity_category_id: int


class HotelAmenityUpdate(MultilingualNameBaseUpdate):
    is_popular: bool | None = None
    payment_type: PaymentType | None = None
    amenity_category_id: int | None = None


class HotelAmenityFilter(BaseModel):
    id: int | None = None
    is_popular: bool | None = None
    hotel_amenity_category_id: int | None = None


# endregion


# region HotelAmenityCategory


class HotelAmenityCategoryCreate(MultilingualNameBase):
    pass


class HotelAmenityCategoryCreate(MultilingualNameBase):
    pass


class HotelAmenityCategoryCreateInternal(BaseModel):
    name: dict[str, str]


class HotelAmenityCategoryUpdate(MultilingualNameBaseUpdate):
    pass


class HotelAmenityCategoryFilter(BaseModel):
    id: int | None = None


# endregion
