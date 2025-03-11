from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.dao.room.amenities import (
    RoomAmenityCategoryDAO,
    RoomAmenityDAO,
)
from app.schemas.room.amenities import (
    RoomAmenityCategoryCreate,
    RoomAmenityCreate,
    RoomAmenityFilter,
    RoomAmenityUpdate,
)

router = APIRouter(
    prefix="/room-amenities",
)


@router.get("/")
async def get_all_room_amenities(
    session=SessionDep,
):
    """
    Все удобства комнат
    """
    return await RoomAmenityDAO.get_all_amenities(
        session=session,
    )


@router.get("/categories")
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


@router.post("/categories")
async def create_room_amenity_category(
    amenity_category_create_data: RoomAmenityCategoryCreate,
    session=TransactionSessionDep,
):
    """
    Создать новую категорию удобств комнат
    """
    return await RoomAmenityCategoryDAO.create(
        session=session,
        values=amenity_category_create_data,
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


@router.post("/categories/{category_id}/amenities")
async def create_room_amenity(
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
        filters=RoomAmenityFilter(
            room_amenity_category_id=category_id,
        ),
    )


@router.patch("/categories/{category_id}/amenities/{amenity_id}")
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
