from fastapi import APIRouter, Depends

from app.api.user.functions.dependencies import get_current_active_auth_user
from app.api.user.schemas import UserRead
from app.core import SessionDep
from app.core.config import settings
from app.dao import CountryDAO

router = APIRouter(
    tags=["Country"],
    prefix=settings.api_v1.country_prefix,
)


@router.get("/")
async def get_countries(
    user: UserRead = Depends(get_current_active_auth_user),
    session=SessionDep,
):
    return await CountryDAO.get_all(
        session=session,
        filters=None,
    )
