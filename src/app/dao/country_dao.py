from sqlalchemy.ext.asyncio import AsyncSession
from app.api.country.models import Country, City
from .base_dao import BaseDAO


class CountryDAO(BaseDAO):
    model = Country


class CityDAO(BaseDAO):
    model = City
