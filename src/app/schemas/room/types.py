from pydantic import BaseModel

from ..mixins import MultilingualNameBase, MultilingualNameBaseUpdate


class RoomTypeBase(MultilingualNameBase):
    pass


class RoomTypeCreate(RoomTypeBase):
    pass


class RoomTypeCreateInternal(BaseModel):
    name: dict[str, str]


class RoomTypeUpdate(MultilingualNameBaseUpdate):
    pass


class RoomTypeUpdateInternal(RoomTypeUpdate):
    pass


class RoomTypeFilter(BaseModel):
    id: int | None = None


class RoomTypeRead(RoomTypeBase):
    id: int
    name: dict[str, str]
