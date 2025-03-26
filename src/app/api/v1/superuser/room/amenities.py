from fastapi import APIRouter, Depends

from app.api.dependencies.amenities import validate_room_amenity
from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.dao.room.amenities import (
    RoomAmenityDAO,
)
from app.schemas.room.amenities import (
    RoomAmenityCreate,
    RoomAmenityFilter,
    RoomAmenityRead,
    RoomAmenityUpdate,
)

router = APIRouter(
    tags=["Superuser Room Amenities"],
    prefix="/room-amenities",
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


@router.post(
    "/categories/{category_id}/amenities",
    dependencies=[Depends(get_current_superuser)],
)
async def create_room_amenity(
    category_id: int,
    amenity_create_data: RoomAmenityCreate,
    session=TransactionSessionDep,
):
    return await RoomAmenityDAO.create(
        session=session,
        values=amenity_create_data,
    )


@router.put(
    "/amenities/{amenity_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def update_room_amenity(
    category_id: int,
    amenity_id: int,
    amenity_update_data: RoomAmenityUpdate,
    room_amenity: RoomAmenityRead = Depends(validate_room_amenity),
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


@router.delete(
    "/amenities/{amenity_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def delete_room_amenity(
    amenity_id: int,
    room_amenity: RoomAmenityRead = Depends(validate_room_amenity),
    session=TransactionSessionDep,
):
    return await RoomAmenityDAO.delete(session=session, filters=amenity_id)
