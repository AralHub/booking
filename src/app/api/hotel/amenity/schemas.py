from pydantic import BaseModel

from .models import PaymentType


class AmenityBase(BaseModel):
    name: str
    description: str
    is_popular: bool
    payment_type: PaymentType


class RoomCreate(AmenityBase):
    pass


class RoomCreateInternal(RoomCreate):
    pass


class RoomUpdate(AmenityBase):
    pass


class RoomUpdateInternal(RoomUpdate):
    pass


class RoomFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    is_popular: bool | None = None
    payment_type: PaymentType | None = None
