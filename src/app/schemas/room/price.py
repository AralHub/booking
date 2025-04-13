from pydantic import BaseModel, ConfigDict

from ..field_validation import GUEST_QUANTITY_FIELD, GUEST_QUANTITY_FIELD_UPDATE


class RoomPriceBase(BaseModel):
    guest_quantity: GUEST_QUANTITY_FIELD
    price: float


class RoomPriceRead(RoomPriceBase):
    id: int
    room_id: int
    model_config = ConfigDict(from_attributes=True)


class RoomPriceCreate(RoomPriceBase):
    pass


class RoomPriceCreateInternal(RoomPriceCreate):
    room_id: int


class RoomPriceUpdate(BaseModel):
    guest_quantity: GUEST_QUANTITY_FIELD_UPDATE
    price: float | None = None


class RoomPriceUpdateInternal(RoomPriceUpdate):
    room_id: int


class RoomPriceFilter(BaseModel):
    id: int | None = None
    room_id: int | None = None
    guest_quantity: int | None = None
    price: float | None = None
