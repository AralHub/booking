from fastapi import APIRouter

from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException

from .dao import CityDAO, CountryDAO, LocationDAO
from .schemas import (
    CityCreate,
    CityCreateInternal,
    CityFilter,
    CityRead,
    CountryCreate,
    CountryFilter,
    CountryUpdate,
    LocationCreate,
    LocationCreateInternal,
    LocationFilter,
    LocationUpdate,
    LocationUpdateInternal,
)

router = APIRouter(
    tags=["Locations"],
)


# region Country
@router.get("/countries")
async def get_countries(
    session=SessionDep,
):
    return await CountryDAO.get_all(
        session=session,
        filters=None,
    )


@router.get("/countries/{country_id}")
async def get_country(
    country_id: int,
    session=SessionDep,
):
    return await CountryDAO.get_one_or_none_by_id(
        session=session,
        data_id=country_id,
    )


@router.post("/countries")
async def add_country(
    country_create_data: CountryCreate,
    session=TransactionSessionDep,
):
    return await CountryDAO.create(
        session=session,
        values=country_create_data,
    )


@router.patch("/countries/{country_id}")
async def update_country(
    country_id: int,
    country_update_data: CountryUpdate,
    session=TransactionSessionDep,
):
    return await CountryDAO.create(
        session=session,
        filters=CountryFilter(id=country_id),
        values=country_update_data,
    )


# endregion


# region City
@router.get("/countries/{country_id}/cities")
async def get_all_cities_by_country_id(
    country_id: int,
    session=SessionDep,
):
    return await CityDAO.get_all(
        session=session,
        filters=CityFilter(country_id=country_id),
    )


@router.post(
    "/countries/{country_id}/cities",
    response_model=CityRead,
)
async def add_city(
    country_id: int,
    city_create_data: CityCreate,
    session=TransactionSessionDep,
):
    create_city_data = CityCreateInternal(
        **city_create_data.model_dump(),
        country_id=country_id,
    )
    return await CityDAO.create(
        session=session,
        values=create_city_data,
    )


# endregion


# region Hotel Location
@router.get("/hotels/{hotel_id}/location")
async def get_hotel_location(
    hotel_id: int,
    session=SessionDep,
):
    db_hotel_location = await LocationDAO.get_one_or_none(
        session=session,
        filters=LocationFilter(
            hotel_id=hotel_id,
        ),
    )
    if not db_hotel_location:
        raise NotFoundException("Hotel location not found")
    return db_hotel_location


@router.post("/hotels/{hotel_id}/location")
async def add_hotel_location(
    hotel_id: int,
    location_create_data: LocationCreate,
    session=TransactionSessionDep,
):
    return await LocationDAO.create(
        session=session,
        values=LocationCreateInternal(
            **location_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


@router.put("/hotels/{hotel_id}/location")
async def update_hotel_location(
    hotel_id: int,
    location_update_data: LocationUpdate,
    session=TransactionSessionDep,
):
    return await LocationDAO.update(
        session=session,
        values=LocationUpdateInternal(
            **location_update_data.model_dump(),
        ),
        filters=LocationFilter(
            hotel_id=hotel_id,
        ),
    )


# endregion
