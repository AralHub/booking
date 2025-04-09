from fastapi import APIRouter, Depends, Query

from app.api.dependencies.location import validate_country
from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import BadRequestException
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    DataResponse,
    ListResponse,
    PaginatedResponse,
)
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
    CountryRead,
    CountryUpdate,
)

router = APIRouter(
    tags=["Superuser Locations"],
)


# region Country
@router.get(
    "/locations/countries",
    response_model=ListResponse[CountryRead],
)
async def get_countries(
    session=SessionDep,
):
    countries = await CountryDAO.get_all(
        session=session,
        filters=None,
    )
    return ListResponse(
        data=[CountryRead.model_validate(country) for country in countries],
        total=len(countries),
    )


@router.post(
    "/locations/countries",
    response_model=DataResponse[CountryRead],
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
    created_country = await CountryDAO.create(
        session=session,
        values=country_create_data,
    )
    return DataResponse(
        data=created_country,
        message=CountryRead.get(
            "DATA_CREATED",
            default="Country created successfully",
        ),
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
    updated_country = await CountryDAO.update(
        session=session,
        filters=CountryFilter(id=country_id),
        values=country_update_data,
    )
    return DataResponse(
        data=updated_country,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            default="Country updated successfully",
        ),
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
    await CountryDAO.delete(
        session=session,
        filters=CountryFilter(id=country_id),
    )
    return DataResponse(
        data={"id": country_id},
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            default="Country deleted successfully",
        ),
    )


# endregion


# region City
@router.get(
    "/locations/countries/{country_id}/cities",
    response_model=PaginatedResponse[CityRead],
)
async def get_all_cities_by_country_id(
    country_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    session=SessionDep,
):
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
    return PaginatedResponse(
        data=[CityRead.model_validate(city) for city in result],
        paginate={
            "page": page,
            "page_size": page_size,
            "total_elements": city_count or 0,
            "total_pages": (city_count or 0) // page_size
            + ((city_count or 0) % page_size > 0),
        },
    )


@router.post(
    "/locations/countries/{country_id}/cities",
    response_model=DataResponse[CityRead],
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
    created_city = await CityDAO.create(
        session=session,
        values=create_city_data,
    )
    return DataResponse(
        data=created_city,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            default="City created successfully",
        ),
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
    updated_city = await CityDAO.update(
        session=session,
        filters=CityFilter(id=city_id),
        values=city_update_data,
    )
    return DataResponse(
        data=updated_city,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            default="City updated successfully",
        ),
    )


@router.delete(
    "/locations/cities/{city_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def delete_city(
    city_id: int,
    session=TransactionSessionDep,
):
    await CityDAO.delete(
        session=session,
        filters=CityFilter(
            id=city_id,
        ),
    )
    return DataResponse(
        data={"id": city_id},
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            default="City deleted successfully",
        ),
    )


# endregion
