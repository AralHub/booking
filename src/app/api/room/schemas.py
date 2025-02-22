from pydantic import BaseModel


# region Room
class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    hotel_id: int
    room_type_id: int


class RoomCreateInternal(RoomCreate):
    pass


class RoomUpdate(RoomBase):
    pass


class RoomUpdateInternal(RoomUpdate):
    pass


class RoomFilter(BaseModel):
    id: int | None = None
    hotel_id: int | None = None
    room_type_id: int | None = None


# endregion


# region RoomType
class RoomTypeBase(BaseModel):
    name: str
    description: str | None = None


class RoomTypeCreate(RoomTypeBase):
    room_id: int


class RoomTypeCreateInternal(RoomTypeCreate):
    pass


class RoomTypeUpdate(RoomTypeBase):
    pass


class RoomTypeUpdateInternal(RoomTypeUpdate):
    pass


class RoomTypeFilter(BaseModel):
    id: int | None = None
    room_id: int | None = None
    name: str | None = None
    description: str | None = None


# endregion
# region Bed
class BedBase(BaseModel): ...


class BedCreate(BedBase):
    pass


class BedCreateInternal(BedCreate):
    pass


class BedUpdate(BedBase):
    pass


class BedUpdateInternal(BedUpdate):
    pass


class BedFilter(BaseModel):
    id: int | None = None


# endregion
