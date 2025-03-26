from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.dao.location import CityDAO, CountryDAO


async def validate_city(
    city_id: int,
    session=SessionDep,
):
    db_city = await CityDAO.get_one_or_none_by_id(
        session=session,
        data_id=city_id,
    )
    if not db_city:
        raise NotFoundException("City not found")
    return db_city


async def validate_country(
    country_id: int,
    session=SessionDep,
):
    db_country = await CountryDAO.get_one_or_none_by_id(
        session=session,
        data_id=country_id,
    )
    if not db_country:
        raise NotFoundException("Country not found")
    return db_country
