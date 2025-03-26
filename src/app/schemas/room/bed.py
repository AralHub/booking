from pydantic import BaseModel, Field

from ..mixins import MultilingualNameBase, MultilingualNameBaseUpdate


# region Bed
class BedBase(MultilingualNameBase):
    pass


class BedTypeCreate(BedBase):
    pass


class BedTypeCreateInternal(BedTypeCreate):
    id: int | None = None
    name: dict[str, str]


class BedTypeUpdate(MultilingualNameBaseUpdate):
    pass


class BedTypeUpdateInternal(BedTypeUpdate):
    name: dict[str, str]


class BedFilter(BaseModel):
    id: int | None = None
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
