from pydantic import BaseModel


class HotelBase(BaseModel):
    name: str
    city_id: int
    country_id: int


class HotelRead(HotelBase):
    id: int


class HotelCreate(BaseModel):
    name: str
    city_id: int


class HotelCreateInternal(HotelCreate):
    pass


class HotelUpdate(BaseModel):
    name: str | None = None
    city_id: int | None = None


class HotelUpdateInternal(HotelUpdate):
    pass


class HotelFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    city: str | None = None
    country: str | None = None
