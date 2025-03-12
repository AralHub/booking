from pydantic import BaseModel


class RoomBase(BaseModel):
    image: str
    quantity: int
    base_price: float
    room_area: float


class RoomCreate(RoomBase):
    room_type_id: int


class RoomCreateInternal(RoomCreate):
    hotel_id: int


class RoomUpdate(BaseModel):
    description: str | None = None
    max_guests: int | None = None
    image: str | None = None
    quantity: int | None = None
    base_price: float | None = None
    room_area: float | None = None
    room_type_id: int | None = None


class RoomUpdateInternal(RoomUpdate):
    pass


class RoomFilter(BaseModel):
    id: int | None = None
    max_guests: int | None = None
    description: str | None = None
    image: str | None = None
    quantity: int | None = None
    base_price: float | None = None
    room_area: float | None = None
    room_type_id: int | None = None
    hotel_id: int | None = None


class RoomSearch(BaseModel):
    guest_count: int
