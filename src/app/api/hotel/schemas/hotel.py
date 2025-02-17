from pydantic import BaseModel


class HotelBase(BaseModel):
    name: str
    city_id: int
    country_id: int


class HotelCreate(HotelBase):
    pass


class HotelCreateInternal(HotelCreate):
    pass


class HotelUpdate(HotelBase):
    pass


class HotelUpdateInternal(HotelUpdate):
    pass


class HotelFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    city: str | None = None
    country: str | None = None
