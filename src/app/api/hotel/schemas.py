from pydantic import BaseModel
from ..locations.shemas import CoordinateCreate


# region Hotel
class HotelBase(BaseModel):
    name: str
    city_id: int
    hotel_category_id: int


class HotelRead(HotelBase):
    id: int


class HotelCreate(HotelBase):
    pass
    coordinate: CoordinateCreate | None = None


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
    hotel_category_id: int | None = None


# endregion


# region Hotel Category
class HotelCategoryBase(BaseModel):
    name: str


class HotelCategoryRead(HotelCategoryBase):
    id: int


class HotelCategoryCreate(HotelCategoryBase):
    pass


class HotelCategoryCreateInternal(HotelCategoryCreate):
    pass


class HotelCategoryUpdate(BaseModel):
    name: str | None = None


class HotelCategoryUpdateInternal(HotelCategoryUpdate):
    pass


class HotelCategoryFilter(BaseModel):
    id: int | None = None
    name: str | None = None


# endregion
