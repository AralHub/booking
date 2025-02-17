from fastapi import APIRouter

from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.dao import CountryDAO

from .shemas import (
    CountryCreate,
    CountryFilter,
    CountryUpdate,
)

router = APIRouter(
    prefix=settings.api_v1.country_prefix,
)


@router.get("/")
async def get_countries(
    session=SessionDep,
):
    return await CountryDAO.get_all(
        session=session,
        filters=None,
    )


@router.get("/{country_id}")
async def get_country_by_id(
    country_id: int,
    session=SessionDep,
):
    return await CountryDAO.get_one_or_none_by_id(
        session=session,
        data_id=country_id,
    )


@router.post("/")
async def add_country(
    country_create_data: CountryCreate,
    session=TransactionSessionDep,
):
    return await CountryDAO.create(
        session=session,
        values=country_create_data,
    )


@router.patch("/{country_id}")
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
