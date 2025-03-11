from pydantic import BaseModel


class HotelImageBase(BaseModel):
    id: int
    image: str
    hotel_id: int


class HotelImageFilter(BaseModel):
    id: int | None = None
    image: str | None = None
    hotel_id: int | None = None
