from pydantic import BaseModel

from ..mixins import MultilingualNameBase, MultilingualNameBaseUpdate


# region RoomAmenity
class RoomAmenityBase(MultilingualNameBase):
    pass


class RoomAmenityRead(BaseModel):
    id: int
    name: dict[str, str]
    icon: str | None = None
    is_popular: bool | None = None
    room_amenity_category_id: int


class RoomAmenityCreate(RoomAmenityBase):
    is_popular: bool


class RoomAmenityCreateInternal(BaseModel):
    name: dict[str, str]
    is_popular: bool = False
    room_id: int | None = None
    room_amenity_category_id: int


class RoomAmenityUpdate(MultilingualNameBaseUpdate):
    is_popular: bool | None = None
    room_amenity_category_id: int | None = None


class RoomAmenityUpdateInternal(RoomAmenityUpdate):
    pass


class RoomAmenityFilter(BaseModel):
    id: int | None = None
    is_popular: bool | None = None
    room_amenity_category_id: int | None = None


# endregion


# region RoomAmenityCategory
class RoomAmenityCategoryBase(MultilingualNameBase):
    pass


class RoomAmenityCategoryCreate(BaseModel):
    name: dict[str, str]


class RoomAmenityCategoryUpdate(MultilingualNameBaseUpdate):
    pass


class RoomAmenityCategoryFilter(BaseModel):
    id: int | None = None


class RoomAmenityCategoryRead(BaseModel):
    id: int
    name: dict[str, str]
    room_amenities: list[RoomAmenityRead]


# endregion


class RoomAmenityAssociationRead(BaseModel):
    id: int
    room_amenity_categories: list[RoomAmenityCategoryRead]
