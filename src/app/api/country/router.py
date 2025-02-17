from fastapi import APIRouter

from app.core import SessionDep
from app.core.config import settings
from app.dao import CountryDAO

router = APIRouter(
    tags=["Country"],
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


@router.get("/")
async def add_country(
    session=SessionDep,
):
    return await CountryDAO.create(
        session=session,
        filters=None,
    )
