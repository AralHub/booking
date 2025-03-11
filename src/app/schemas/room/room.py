from pydantic import BaseModel, Field


# region Bed
class BedBase(BaseModel):
    name: str


class BedTypeCreate(BedBase):
    pass


class BeTypeCreateInternal(BedTypeCreate):
    pass


class BedTypeUpdate(BedBase):
    pass


class BedTypeUpdateInternal(BedTypeUpdate):
    pass


class BedFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    bed_type_id: int | None = None


# endregion
# region BedConf
class BedConfCreate(BaseModel):
    bed_type_id: int = Field(..., description="ID типа кровати")
    quantity: int = Field(..., gt=0, description="Количество кроватей данного типа")


class RoomBedConfCreate(BaseModel):
    bed_configurations: list[BedConfCreate]


class RoomBedConfCreateInternal(BedConfCreate):
    room_id: int


class RoomBedConfFilter(BaseModel):
    id: int | None = None
    quantity: int | None = None
    room_id: int | None = None


# endregion


# region Room
class RoomBase(BaseModel):
    image: str
    quantity: int
    base_price: float
    room_area: float


class RoomCreate(RoomBase):
    room_type_id: int


class RoomCreateInternal(RoomCreate):
    hotel_id: int


class RoomUpdate(BaseModel):
    description: str | None = None
    max_guests: int | None = None
    image: str | None = None
    quantity: int | None = None
    base_price: float | None = None
    room_area: float | None = None
    room_type_id: int | None = None


class RoomUpdateInternal(RoomUpdate):
    pass


class RoomFilter(BaseModel):
    id: int | None = None
    max_guests: int | None = None
    description: str | None = None
    image: str | None = None
    quantity: int | None = None
    base_price: float | None = None
    room_area: float | None = None
    room_type_id: int | None = None
    hotel_id: int | None = None


class RoomSearch(BaseModel):
    guest_count: int


# endregion

