from pydantic import BaseModel


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
