from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from ..field_validation import zero_to_none


class RoomBase(BaseModel):
    quantity: int
    base_price: float
    room_area: float


class RoomRead(RoomBase):
    id: int
    image: str | None = None
    hotel_id: int
    max_guests: int
    room_type_id: int
    model_config = ConfigDict(from_attributes=True)


class RoomCreate(RoomBase):
    max_guests: int
    room_type_id: int


class RoomCreateInternal(RoomCreate):
    hotel_id: int


class RoomUpdate(BaseModel):
    max_guests: int | None = None
    image: str | None = None
    quantity: int | None = None
    base_price: float | None = None
    room_area: float | None = None
    room_type_id: int | None = None

    @field_validator("room_type_id")
    def validate_and_sanitize_path(cls, v: int | None) -> int | None:
        return zero_to_none(v)


class RoomUpdateInternal(RoomUpdate):
    use_dinamic_price: bool | None = None


class RoomFilter(BaseModel):
    id: int | None = None
    max_guests: int | None = None
    description: str | None = None
    image: str | None = None
    quantity: int | None = None
    base_price: float | None = None
    room_area: float | None = None
    use_dinamic_price: bool | None = None
    room_type_id: int | None = None
    hotel_id: int | None = None


class RoomSearch(BaseModel):
    check_in: date
    check_out: date
    guests: list[int]
