from pydantic import BaseModel


# region Room
class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    hotel_id: int
    room_type_id: int
    room_amenities: list[int]


class RoomCreateInternal(RoomCreate):
    pass


class RoomUpdate(BaseModel):
    name: str | None = None
    room_type_id: int | None = None
    room_amenities: list[int] | None = None


class RoomUpdateInternal(RoomUpdate):
    pass


class RoomFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    max_guests: int | None = None
    max_children: int | None = None
    description: str | None = None
    preview_photo_url: str | None = None
    quantity: int | None = None
    price_per_night: float | None = None
    room_area: float | None = None
    bed_type_id: int | None = None
    room_type_id: int | None = None
    hotel_id: int | None = None


# endregion


# region RoomType
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


# endregion
# region RoomTypeVariant
class RoomTypeVariantBase(BaseModel):
    name: str


class RoomTypeVariantCreate(RoomTypeVariantBase):
    pass


class RoomTypeVariantCreateInternal(RoomTypeVariantCreate):
    room_type_id: int


class RoomTypeVariantUpdate(BaseModel):
    name: str | None = None


class RoomTypeVariantUpdateInternal(RoomTypeVariantUpdate):
    pass


class RoomTypeVariantFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    room_type_id: int | None = None


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
