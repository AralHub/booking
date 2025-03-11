from app.core.dao import BaseDAO
from app.models.location import City, Country


class CountryDAO(BaseDAO):
    model = Country


class CityDAO(BaseDAO):
    model = City
