from pydantic import BaseModel, field_validator

from ..field_validation import (
    LAT_FIELD,
    LAT_FIELD_UPDATE,
    LONG_FIELD,
    LONG_FIELD_UPDATE,
    zero_to_none,
)


class LocationCreate(BaseModel):
    address: str
    city_id: int
    longitude: LONG_FIELD
    latitude: LAT_FIELD


class LocationCreateInternal(LocationCreate):
    to_airport: float | None = None
    to_railway: float | None = None
    to_city_center: float | None = None
    hotel_id: int


class LocationUpdate(BaseModel):
    address: str | None = None
    latitude: LAT_FIELD_UPDATE = None
    longitude: LONG_FIELD_UPDATE = None
    city_id: int | None = None

    @field_validator("city_id")
    def validate_and_sanitize_path(cls, v: int | None) -> int | None:
        return zero_to_none(v)


class LocationUpdateInternal(LocationUpdate):
    to_airport: float | None = None
    to_railway: float | None = None
    to_city_center: float | None = None


class LocationFilter(BaseModel):
    id: int | None = None
    hotel_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    city_id: int | None = None
