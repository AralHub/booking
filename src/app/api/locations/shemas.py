from pydantic import BaseModel


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
