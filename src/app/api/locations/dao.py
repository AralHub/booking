# from sqlalchemy.ext.asyncio import AsyncSession
from app.api.locations.models import City, Location, Country
from app.core.dao import BaseDAO


class CountryDAO(BaseDAO):
    model = Country


class CityDAO(BaseDAO):
    model = City


class LocationDAO(BaseDAO):
    model = Location
