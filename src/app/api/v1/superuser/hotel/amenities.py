from fastapi import APIRouter, Depends

from app.api.dependencies.user import get_current_superadmin_user
from app.core import SessionDep, TransactionSessionDep
from app.dao.hotel.amenities import (
    HotelAmenityCategoryDAO,
    HotelAmenityDAO,
)
from app.schemas.hotel.amenities import (
    HotelAmenityFilter,
    HotelAmenityUpdate,
)

router = APIRouter(
    tags=["Superuser Hotel Amenities"],
    prefix="/hotel-amenities",
)


@router.get("/")
async def get_all_hotel_amenities(
    session=SessionDep,
):
    """
    Все удобства отеля разделенные по категориям
    """
    return await HotelAmenityCategoryDAO.get_all_amenities(
        session=session,
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


@router.put(
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
