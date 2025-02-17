from fastapi import APIRouter, Depends

from app.api.user.functions.dependencies import get_current_active_auth_user
from app.api.user.schemas import UserRead
from app.core import SessionDep
from app.core.config import settings
from app.dao import HotelDAO

router = APIRouter(
    tags=["Hotel"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get("/")
async def get_hotels(
    user: UserRead = Depends(get_current_active_auth_user),
    session=SessionDep,
):
    return await HotelDAO.get_all(
        session=session,
        filters=None,
    )
