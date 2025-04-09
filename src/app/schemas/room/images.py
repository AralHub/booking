from pydantic import BaseModel


class RoomImageBase(BaseModel):
    image: str
    room_id: int


class RoomImageFilter(BaseModel):
    id: int | None = None
    image: str | None = None
    room_id: int | None = None


class RoomImageRead(RoomImageBase):
    id: int
