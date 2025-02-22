from pydantic import BaseModel


class ImageBase(BaseModel):
    id: int
    image: str
    hotel_id: int


class ImageFilter(BaseModel):
    id: int | None = None
    image: str | None = None
    hotel_id: int | None = None
