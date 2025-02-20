from pydantic import BaseModel, Field


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


# endregion


# region Location
class LocationCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class LocationCreateInternal(LocationCreate):
    pass


class LocationUpdate(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class LocationUpdateInternal(LocationUpdate):
    pass


class LocationFilter(BaseModel):
    id: int | None = None
    latitude: float | None = None
    longitude: float | None = None


# endregion
