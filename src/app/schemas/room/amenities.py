from pydantic import BaseModel, ConfigDict

from ..mixins import MultilingualNameBase, MultilingualNameBaseUpdate


# region RoomAmenity
class RoomAmenityBase(MultilingualNameBase):
    pass


class RoomAmenityRead(BaseModel):
    id: int
    name: dict[str, str]
    icon: str | None = None
    room_amenity_category_id: int


class RoomAmenityCreate(RoomAmenityBase):
    pass


class RoomAmenityCreateInternal(BaseModel):
    name: dict[str, str]
    room_id: int | None = None
    room_amenity_category_id: int


class RoomAmenityUpdate(MultilingualNameBaseUpdate):
    room_amenity_category_id: int | None = None


class RoomAmenityUpdateInternal(BaseModel):
    name: dict[str, str]
    room_amenity_category_id: int | None = None


class RoomAmenityFilter(BaseModel):
    id: int | None = None
    room_amenity_category_id: int | None = None


# endregion


# region RoomAmenityCategory
class RoomAmenityCategoryBase(MultilingualNameBase):
    pass


class RoomAmenityCategoryCreate(RoomAmenityCategoryBase):
    pass


class RoomAmenityCategoryCreateInternal(BaseModel):
    name: dict[str, str]


class RoomAmenityCategoryUpdate(MultilingualNameBaseUpdate):
    pass


class RoomAmenityCategoryFilter(BaseModel):
    id: int | None = None


class RoomAmenityCategoryRead(BaseModel):
    id: int
    name: dict[str, str]
    room_amenities: list[RoomAmenityRead] | None = None
    model_config = ConfigDict(from_attributes=True)


# endregion


class RoomAmenityAssociationRead(BaseModel):
    id: int
    room_amenity_categories: list[RoomAmenityCategoryRead]
