from pydantic import BaseModel


class CountryFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    code: str | None = None


class CityFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    country_id: int | None = None
