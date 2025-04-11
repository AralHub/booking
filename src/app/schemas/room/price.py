from pydantic import BaseModel, ConfigDict


class RoomPriceBase(BaseModel):
    guest_quantity: int
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
    guest_quantity: int | None = None
    price: float | None = None


class RoomPriceUpdateInternal(RoomPriceUpdate):
    room_id: int


class RoomPriceFilter(BaseModel):
    id: int | None = None
    room_id: int | None = None
    guest_quantity: int | None = None
    price: float | None = None
