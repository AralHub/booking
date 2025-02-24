from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep

from .dao import (
    RoomAmenityCategoryDAO,
    RoomAmenityDAO,
)
from .schemas import (
    RoomAmenityCreate,
    RoomAmenityFilter,
)

router = APIRouter(
    tags=["Room Amenities"],
    prefix="/hotels/rooms",
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


@router.get("/amenities/")
async def get_all_room_amenities(
    session=SessionDep,
):
    """
    Все удобства комнат
    """
    return await RoomAmenityDAO.get_all_amenities(
        session=session,
    )


@router.post("/amenity-categories/{category_id}/amenities")
async def create_hotel_amenity(
    category_id: int,
    amenity_create_data: RoomAmenityCreate,
    session=TransactionSessionDep,
):
    """
    Создать новое удобство в категории
    """
    return await RoomAmenityDAO.create(
        session=session,
        values=amenity_create_data,
        filters=RoomAmenityFilter(hotel_amenity_category_id=category_id),
    )


@router.patch("/amenity-categories/{category_id}/amenities/{amenity_id}")
async def update_hotel_amenity(
    category_id: int,
    amenity_id: int,
    amenity_update_data: RoomAmenityUpdate,
    session=TransactionSessionDep,
):
    """
    Обновить удобство в категории
    """
    return await RoomAmenityDAO.update(
        session=session,
        filters=RoomAmenityFilter(
            id=amenity_id,
            hotel_amenity_category_id=category_id,
        ),
        values=amenity_update_data,
    )
