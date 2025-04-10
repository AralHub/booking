from pydantic import BaseModel, field_validator

from ..field_validation import (
    LAT_FIELD,
    LAT_FIELD_UPDATE,
    LONG_FIELD,
    LONG_FIELD_UPDATE,
    zero_to_none,
)


class Coordinates(BaseModel):
    longitude: LONG_FIELD
    latitude: LAT_FIELD


class LocationRead(BaseModel):
    id: int
    hotel_id: int
    address: str
    city: str
    coordinates: Coordinates
    to_airport: float | None = None
    to_railway: float | None = None
    to_city_center: float | None = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_city(cls, obj, city_name=None):
        return cls(
            id=obj.id,
            hotel_id=obj.hotel_id,
            address=obj.address,
            city_id=obj.city_id,
            coordinates=Coordinates(
                longitude=obj.longitude,
                latitude=obj.latitude,
            ),
            to_airport=obj.to_airport,
            to_railway=obj.to_railway,
            to_city_center=obj.to_city_center,
            city=city_name,
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
