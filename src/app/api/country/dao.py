# from sqlalchemy.ext.asyncio import AsyncSession
from app.api.country.models import City, Country
from app.core.dao import BaseDAO


class CountryDAO(BaseDAO):
    model = Country


class CityDAO(BaseDAO):
    model = City
