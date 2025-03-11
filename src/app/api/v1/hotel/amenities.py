from fastapi import APIRouter, Depends

from app.api.dependencies.user import get_current_superadmin_user
from app.core import SessionDep, TransactionSessionDep
from app.dao.hotel.amenities import (
    HotelAmenityCategoryDAO,
    HotelAmenityDAO,
)
from app.schemas.hotel.amenities import (
    HotelAmenityCategoryCreate,
    HotelAmenityCreate,
    HotelAmenityFilter,
    HotelAmenityUpdate,
)

router = APIRouter(
    prefix="/hotel-amenities",
)


@router.get("/")
async def get_all_hotel_amenities(
    session=SessionDep,
):
    """
    Все удобства отеля c разделенные по категориям
    """
    return await HotelAmenityDAO.get_all_amenities(session=session)


@router.get("/categories")
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


@router.post(
    "/categories",
    dependencies=[Depends(get_current_superadmin_user)],
)
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


@router.get(
    "/categories/{category_id}/amenities",
    dependencies=[Depends(get_current_superadmin_user)],
)
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


@router.post(
    "/categories/{category_id}/amenities",
    dependencies=[Depends(get_current_superadmin_user)],
)
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


@router.patch(
    "/categories/{category_id}/amenities/{amenity_id}",
    dependencies=[Depends(get_current_superadmin_user)],
)
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
