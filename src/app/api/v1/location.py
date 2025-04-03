from fastapi import APIRouter, Depends

from app.api.dependencies.location import validate_country
from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import BadRequestException
from app.dao.location import CityDAO, CountryDAO
from app.schemas.location import (
    CityCreate,
    CityCreateInternal,
    CityFilter,
    CityRead,
    CityUpdate,
    CountryBase,
    CountryCreate,
    CountryFilter,
    CountryUpdate,
)
from app.schemas.field_validation import Page

router = APIRouter(
    tags=["Superuser Locations"],
)


# region Country
@router.get("/locations/countries")
async def get_countries(
    session=SessionDep,
):
    return await CountryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post(
    "/locations/countries",
    dependencies=[Depends(get_current_superuser)],
)
async def add_country(
    country_create_data: CountryCreate,
    session=TransactionSessionDep,
):
    db_country = await CountryDAO.get_one_or_none(
        session=session,
        filters=CountryFilter(
            name=country_create_data.name,
        ),
    )
    if db_country:
        raise BadRequestException("Country already exists")
    return await CountryDAO.create(
        session=session,
        values=country_create_data,
    )


@router.put(
    "/locations/countries/{country_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def update_country(
    country_id: int,
    country_update_data: CountryUpdate,
    country: CountryBase = Depends(validate_country),
    session=TransactionSessionDep,
):
    db_country = await CountryDAO.get_one_or_none(
        session=session,
        filters=CountryFilter(
            name=country_update_data.name,
        ),
    )
    if db_country and db_country.id != country_id:
        raise BadRequestException(
            f"Country with name {country_update_data.name} already exists"
        )
    return await CountryDAO.update(
        session=session,
        filters=CountryFilter(id=country_id),
        values=country_update_data,
    )


@router.delete(
    "/locations/countries/{country_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def delete_country(
    country_id: int,
    country: CountryBase = Depends(validate_country),
    session=TransactionSessionDep,
):
    return await CountryDAO.delete(
        session=session,
        filters=CountryFilter(id=country_id),
    )


# endregion


# region City
@router.get("/locations/countries/{country_id}/cities")
async def get_all_cities_by_country_id(
    country_id: int,
    page: int = 1,
    page_size: int = 10,
    session=SessionDep,
):
    # return await CityDAO.get_all(
    #     session=session,
    #     filters=CityFilter(country_id=country_id),
    # )
    city_count = await CityDAO.count(
        session=session,
        filters=CityFilter(country_id=country_id),
    )
    result = await CityDAO.paginate(
        session=session,
        page=page,
        page_size=page_size,
        filters=CityFilter(country_id=country_id),
        order_by="id",
        order_direction="desc",
    )
    return Page(
        page=page,
        page_size=page_size,
        total_elements=city_count or 0,
        total_pages=(city_count or 0) // page_size
        + ((city_count or 0) % page_size > 0),
        content=[CityRead.model_validate(city) for city in result],
    )


@router.post(
    "/locations/countries/{country_id}/cities",
    response_model=CityRead,
    dependencies=[Depends(get_current_superuser)],
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


@router.put(
    "/locations/cities/{city_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def update_city(
    city_id: int,
    city_update_data: CityUpdate,
    session=TransactionSessionDep,
):
    return await CityDAO.update(
        session=session,
        filters=CityFilter(id=city_id),
        values=city_update_data,
    )


@router.delete(
    "/locations/cities/{city_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def delete_city(
    city_id: int,
    session=TransactionSessionDep,
):
    return await CityDAO.delete(
        session=session,
        filters=CityFilter(
            id=city_id,
        ),
    )


# endregion
