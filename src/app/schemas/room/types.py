from pydantic import BaseModel


class RoomTypeBase(BaseModel):
    name: str


class RoomTypeCreate(RoomTypeBase):
    pass


class RoomTypeCreateInternal(RoomTypeCreate):
    pass


class RoomTypeUpdate(BaseModel):
    name: str | None = None


class RoomTypeUpdateInternal(RoomTypeUpdate):
    pass


class RoomTypeFilter(BaseModel):
    id: int | None = None
    name: str | None = None
