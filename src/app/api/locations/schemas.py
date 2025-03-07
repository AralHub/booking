from typing import Annotated

from pydantic import BaseModel, Field

LONG_FIELD = Annotated[
    float | None,
    Field(
        ge=-180,
        le=180,
        default=None,
    ),
]
LAT_FIELD = Annotated[
    float | None,
    Field(
        ge=-90,
        le=90,
        default=None,
    ),
]


# region Country
class CountryBase(BaseModel):
    name: str
    code: str


class CountryCreate(CountryBase):
    pass


class CountryCreateInternal(CountryCreate):
    pass


class CountryUpdate(CountryBase):
    pass


class CountryUpdateInternal(CountryUpdate):
    pass


class CountryFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    code: str | None = None


# endregion

# region City


class CityBase(BaseModel):
    name: str
    country_id: int


class CityRead(CityBase):
    id: int


class CityCreate(BaseModel):
    name: str


class CityCreateInternal(CityCreate):
    country_id: int


class CityUpdate(BaseModel):
    name: str | None = None


class CityUpdateInternal(CityUpdate):
    country_id: int


class CityFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    country_id: int | None = None
    slug: str | None = None
    properties_count: int | None = None
    image: str | None = None
    aero_lat: float | None = None
    aero_lng: float | None = None
    rail_lat: float | None = None
    rail_lng: float | None = None
    geocode_lng: float | None = None
    geocode_lat: float | None = None


# endregion


# region Location
class LocationCreate(BaseModel):
    address: str
    city_id: int
    longitude: LONG_FIELD
    latitude: LAT_FIELD


class LocationCreateInternal(LocationCreate):
    to_airport: float
    to_railway: float
    to_city_center: float
    hotel_id: int


class LocationUpdate(BaseModel):
    address: str
    latitude: float | None = None
    longitude: float | None = None
    city_id: int | None = None


class LocationUpdateInternal(LocationUpdate):
    to_airport: float | None = None
    to_railway: float | None = None
    to_city_center: float | None = None


class LocationFilter(BaseModel):
    id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    hotel_id: int | None = None
    city_id: int | None = None


# endregion


class Coordinates(BaseModel):
    longitude: LONG_FIELD
    latitude: LAT_FIELD

    def to_string(self) -> str:
        return f"{self.longitude},{self.latitude}"


class RoutePoint(BaseModel):
    coordinates: Coordinates
    name: str


class RouteRequest(BaseModel):
    points: list[RoutePoint] = Field(..., min_length=2)

    def get_coordinates_string(self) -> str:
        return ";".join(point.coordinates.to_string() for point in self.points)


class DistanceResponse(BaseModel):
    distance: float
    duration: float


class RouteSegment(DistanceResponse):
    start_point: RoutePoint
    end_point: RoutePoint


class RouteResponse(BaseModel):
    segments: list[RouteSegment]
    total_distance: float
    total_duration: float
