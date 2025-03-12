from fastapi import APIRouter, Depends

from app.api.dependencies.user import get_current_superadmin_user
from app.core import SessionDep, TransactionSessionDep
from app.dao.room.amenities import (
    RoomAmenityCategoryDAO,
    RoomAmenityDAO,
)
from app.schemas.room.amenities import (
    RoomAmenityFilter,
    RoomAmenityUpdate,
)

router = APIRouter(
    tags=["Superuser Room Amenities"],
    prefix="/room-amenities",
)


@router.get("")
async def get_room_amenities(
    session=SessionDep,
):
    """
    Все удобства комнат разделенные по категориям
    """
    return await RoomAmenityCategoryDAO.get_all_amenities(
        session=session,
    )


@router.get("/categories/{category_id}/amenities")
async def get_room_amenities_by_category(
    category_id: int,
    session=SessionDep,
):
    """
    Удобства по категории-удобств комнат
    """
    return await RoomAmenityDAO.get_all(
        session=session,
        filters=RoomAmenityFilter(room_amenity_category_id=category_id),
    )


@router.put(
    "/categories/{category_id}/amenities/{amenity_id}",
    dependencies=[Depends(get_current_superadmin_user)],
)
async def update_room_amenity(
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
            room_amenity_category_id=category_id,
        ),
        values=amenity_update_data,
    )
