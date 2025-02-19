from pydantic import BaseModel

from .models import PaymentType


class AmenityBase(BaseModel):
    name: str
    description: str


class AmenityCreate(AmenityBase):
    is_popular: bool
    payment_type: PaymentType
    amenity_category_id: int


class AmenityCreateInternal(AmenityCreate):
    hotel_id: int | None = None


class AmenityUpdate(AmenityBase):
    is_popular: bool | None = None
    payment_type: PaymentType | None = None
    amenity_category_id: int | None = None


class AmenityUpdateInternal(AmenityUpdate):
    pass


class AmenityFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    is_popular: bool | None = None
    payment_type: PaymentType | None = None


class AmenityCategoryBase(BaseModel):
    name: str


class AmenityCategoryCreate(AmenityCategoryBase):
    pass


class AmenityCategoryCreateInternal(AmenityCategoryCreate):
    pass


class AmenityCategoryUpdate(AmenityCategoryBase):
    pass


class AmenityCategoryUpdateInternal(AmenityCategoryUpdate):
    pass


class AmenityCategoryFilter(BaseModel):
    id: int | None = None
    name: str | None = None
