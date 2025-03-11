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
