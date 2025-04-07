from pydantic import BaseModel, ConfigDict, Field


# region Country
class CountryBase(BaseModel):
    name: str
    code: str


class CountryRead(CountryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


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
    model_config = ConfigDict(from_attributes=True)
    id: int
    country_id: int
    slug: str
    properties_count: int | None = None
    image: str | None = None
    aero_lat: float
    aero_lng: float
    rail_lat: float
    rail_lng: float
    geocode_lng: float
    geocode_lat: float


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


# region Coordinates


class Coordinates(BaseModel):
    longitude: float
    latitude: float

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


# endregion
