from pydantic import BaseModel

from app.models.hotel.amenities import PaymentType


# region HotelAmenity
class HotelAmenityBase(BaseModel):
    name: str
    description: str


class HotelAmenityCreate(HotelAmenityBase):
    is_popular: bool
    payment_type: PaymentType
    amenity_category_id: int


class HotelAmenityCreateInternal(HotelAmenityCreate):
    hotel_id: int | None = None


class HotelAmenityUpdate(HotelAmenityBase):
    is_popular: bool | None = None
    payment_type: PaymentType | None = None
    amenity_category_id: int | None = None


class HotelAmenityUpdateInternal(HotelAmenityUpdate):
    pass


class HotelAmenityFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    is_popular: bool | None = None
    payment_type: PaymentType | None = None
    hotel_amenity_category_id: int | None = None


# endregion


# region HotelAmenityCategory
class HotelAmenityCategoryBase(BaseModel):
    name: str


class HotelAmenityCategoryCreate(HotelAmenityCategoryBase):
    pass


class HotelAmenityCategoryCreateInternal(HotelAmenityCategoryCreate):
    pass


class HotelAmenityCategoryUpdate(HotelAmenityCategoryBase):
    pass


class HotelAmenityCategoryUpdateInternal(HotelAmenityCategoryUpdate):
    pass


class HotelAmenityCategoryFilter(BaseModel):
    id: int | None = None
    name: str | None = None


# endregion
