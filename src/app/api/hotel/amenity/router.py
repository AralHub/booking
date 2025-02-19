from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep
from app.core.config import settings

from .dao import AmenityDAO

router = APIRouter(
    tags=["Amenity"],
    prefix=settings.api_v1.amenity_prefix,
)


@router.get("/")
async def get_amenities(
    session=SessionDep,
):
    return await AmenityDAO.get_all(
        session=session,
        filters=None,
    )
