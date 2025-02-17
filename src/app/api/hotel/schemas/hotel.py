from pydantic import BaseModel


class HotelFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    city: str | None = None
    country: str | None = None
