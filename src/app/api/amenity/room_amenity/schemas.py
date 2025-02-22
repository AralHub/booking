from pydantic import BaseModel


# region RoomAmenity
class RoomAmenityBase(BaseModel):
    name: str


class RoomAmenityCreate(RoomAmenityBase):
    is_popular: bool


class RoomAmenityCreateInternal(RoomAmenityCreate):
    room_id: int | None = None


class RoomAmenityUpdate(RoomAmenityBase):
    is_popular: bool | None = None


class RoomAmenityUpdateInternal(RoomAmenityUpdate):
    pass


class RoomAmenityFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    is_popular: bool | None = None


# endregion


# region RoomAmenityCategory
class RoomAmenityCategoryBase(BaseModel):
    name: str


class RoomAmenityCategoryCreate(RoomAmenityCategoryBase):
    pass


class RoomAmenityCategoryCreateInternal(RoomAmenityCategoryCreate):
    pass


class RoomAmenityCategoryUpdate(RoomAmenityCategoryBase):
    pass


class RoomAmenityCategoryUpdateInternal(RoomAmenityCategoryUpdate):
    pass


class RoomAmenityCategoryFilter(BaseModel):
    id: int | None = None
    name: str | None = None


# endregion
