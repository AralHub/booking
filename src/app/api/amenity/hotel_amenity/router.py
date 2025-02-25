from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep

from .dao import (
    HotelAmenityCategoryDAO,
    HotelAmenityDAO,
)
from .schemas import (
    HotelAmenityCategoryCreate,
    HotelAmenityCreate,
    HotelAmenityFilter,
    HotelAmenityUpdate,
)

router = APIRouter(
    prefix="/hotels",
    tags=["Hotel Amenities"],
)


# region Hotel Amenity Category
@router.get("/amenity-categories")
async def get_hotel_amenity_categories(
    session=SessionDep,
):
    """
    Все категории-удобств отеля
    """
    return await HotelAmenityCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.get("/amenity-categories/{category_id}")
async def get_hotel_amenity_category(
    category_id: int,
    session=SessionDep,
):
    """
    Получить категорию удобств отеля по ID
    """
    return await HotelAmenityCategoryDAO.get_one_or_none(
        session=session,
        filters=HotelAmenityFilter(id=category_id),
    )


@router.post("/amenity-categories")
async def create_hotel_amenity_category(
    amenity_category_create_data: HotelAmenityCategoryCreate,
    session=TransactionSessionDep,
):
    """
    Создать новую категорию удобств отеля
    """
    return await HotelAmenityCategoryDAO.create(
        session=session,
        values=amenity_category_create_data,
    )


@router.get("/amenity-categories/{category_id}/amenities")
async def get_hotel_amenities_by_category(
    category_id: int,
    session=SessionDep,
):
    """
    Удобства по категории-удобств отеля
    """
    return await HotelAmenityDAO.get_all(
        session=session,
        filters=HotelAmenityFilter(hotel_amenity_category_id=category_id),
    )


@router.post("/amenity-categories/{category_id}/amenities")
async def create_hotel_amenity(
    category_id: int,
    amenity_create_data: HotelAmenityCreate,
    session=TransactionSessionDep,
):
    """
    Создать новое удобство в категории
    """
    return await HotelAmenityDAO.create(
        session=session,
        values=amenity_create_data,
        filters=HotelAmenityFilter(
            hotel_amenity_category_id=category_id,
        ),
    )


@router.patch("/amenity-categories/{category_id}/amenities/{amenity_id}")
async def update_hotel_amenity(
    category_id: int,
    amenity_id: int,
    amenity_update_data: HotelAmenityUpdate,
    session=TransactionSessionDep,
):
    """
    Обновить удобство в категории
    """
    return await HotelAmenityDAO.update(
        session=session,
        filters=HotelAmenityFilter(
            id=amenity_id,
            hotel_amenity_category_id=category_id,
        ),
        values=amenity_update_data,
    )


@router.get("/amenities")
async def get_all_hotel_amenities(
    session=SessionDep,
):
    """
    Все удобства отеля c разделенные по категориям
    """
    return await HotelAmenityDAO.get_all_amenities(session=session)


# endregion
