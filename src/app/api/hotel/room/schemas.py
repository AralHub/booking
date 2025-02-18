from pydantic import BaseModel


class RoomBase(BaseModel):
    name: str
    hotel_id: int


class RoomCreate(RoomBase):
    pass


class RoomCreateInternal(RoomCreate):
    pass


class RoomUpdate(RoomBase):
    pass


class RoomUpdateInternal(RoomUpdate):
    pass


class RoomFilter(BaseModel):
    id: int | None = None
    hotel_id: int | None = None
