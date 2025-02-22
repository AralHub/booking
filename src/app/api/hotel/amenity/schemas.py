from pydantic import BaseModel

from .models import PaymentType


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


# region RoomAmenity
class RoomAmenityBase(BaseModel):
    name: str


class RoomAmenityCreate(RoomAmenityBase):
    is_popular: bool


class RoomAmenityCreateInternal(RoomAmenityCreate):
    room_id: int | None = None


class RoomAmenityUpdate(RoomAmenityBase):
    is_popular: bool | None = None


class RoomAmenityUpdateInternal(RoomAmenityUpdate):
    pass


class RoomAmenityFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    is_popular: bool | None = None


# endregion


# region RoomAmenityCategory
class RoomAmenityCategoryBase(BaseModel):
    name: str


class RoomAmenityCategoryCreate(RoomAmenityCategoryBase):
    pass


class RoomAmenityCategoryCreateInternal(RoomAmenityCategoryCreate):
    pass


class RoomAmenityCategoryUpdate(RoomAmenityCategoryBase):
    pass


class RoomAmenityCategoryUpdateInternal(RoomAmenityCategoryUpdate):
    pass


class RoomAmenityCategoryFilter(BaseModel):
    id: int | None = None
    name: str | None = None


# endregion
