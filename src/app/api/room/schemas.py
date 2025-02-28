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


# endregion
# region BedConf
class BedConfCreate(BaseModel):
    bed_type_id: int = Field(..., description="ID типа кровати")
    quantity: int = Field(..., gt=0, description="Количество кроватей данного типа")


class RoomBedConfUpdate(BaseModel):
    bed_configurations: list[BedConfCreate]


class RoomBedConfUpdateInternal(BaseModel):
    room_id: int


# endregion


# region Room
class RoomBase(BaseModel):
    max_children: int
    description: str | None = None
    image: str
    quantity: int
    price_per_night: float
    room_area: float


class RoomCreate(BaseModel):
    room_type_variant_id: int
    quantity: int
    max_guests: int
    room_amenities: list[int] | None = []
    room_area: float | None = None


class RoomCreateInternal(RoomCreate):
    hotel_id: int


class RoomUpdate(BaseModel):
    room_amenities: list[int] | None = None
    max_guests: int | None = None
    max_children: int | None = None
    description: str | None = None
    image: str | None = None
    quantity: int | None = None
    price_per_night: float | None = None
    room_area: float | None = None
    bed_type_id: int | None = None
    room_type_variant_id: int | None = None
    hotel_id: int | None = None


class RoomUpdateInternal(RoomUpdate):
    pass


class RoomFilter(BaseModel):
    id: int | None = None
    max_guests: int | None = None
    max_children: int | None = None
    description: str | None = None
    image: str | None = None
    quantity: int | None = None
    price_per_night: float | None = None
    room_area: float | None = None
    bed_type_id: int | None = None
    room_type_variant_id: int | None = None
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
