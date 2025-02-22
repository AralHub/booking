from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep

from .dao import (
    RoomAmenityCategoryDAO,
    RoomAmenityDAO,
)

router = APIRouter(
    tags=["Room Amenities"],
    prefix="/hotels/rooms",
)


@router.get("/amenities/")
async def get_all_room_amenities(
    session=SessionDep,
):
    """
    Все удобства комнат
    """
    return await RoomAmenityDAO.get_all(
        session=session,
        filters=None,
    )


@router.get("/amenity-categories/")
async def get_all_room_amenity_categories(
    session=SessionDep,
):
    """
    Все категории-удобств комнат
    """
    return await RoomAmenityCategoryDAO.get_all(
        session=session,
        filters=None,
    )
