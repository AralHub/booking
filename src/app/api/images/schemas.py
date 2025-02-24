from pydantic import BaseModel


class HotelImageBase(BaseModel):
    id: int
    image: str
    hotel_id: int


class HotelImageFilter(BaseModel):
    id: int | None = None
    image: str | None = None
    hotel_id: int | None = None


class RoomImageBase(BaseModel):
    id: int
    image: str
    room_id: int


class RoomImageFilter(BaseModel):
    id: int | None = None
    image: str | None = None
    room_id: int | None = None
