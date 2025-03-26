from fastapi import APIRouter, Depends

from app.api.dependencies.amenities import validate_hotel_amenities_category
from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.dao.hotel.amenities import (
    HotelAmenityCategoryDAO,
    HotelAmenityDAO,
)
from app.schemas.hotel.amenities import (
    HotelAmenityCategoryCreate,
    HotelAmenityCategoryCreateInternal,
    HotelAmenityCategoryFilter,
    HotelAmenityCategoryUpdate,
    HotelAmenityCreate,
    HotelAmenityCreateInternal,
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


@router.post("/categories/{category_id}/amenities")
async def create_hotel_amenity(
    hotel_amenity_category_id: int,
    hotel_amenity_data: HotelAmenityCreate,
    session=TransactionSessionDep,
):
    """
    Удобства по категории-удобств отеля
    """
    return await HotelAmenityDAO.create(
        session=session,
        values=HotelAmenityCreateInternal(
            name=hotel_amenity_data.to_dict_name(),
            hotel_amenity_category_id=hotel_amenity_category_id,
        ),
    )


@router.put(
    "/amenities/{amenity_id}",
    dependencies=[Depends(get_current_superuser)],
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


@router.delete("/amenities/{amenity_id}")
async def delete_hotel_amenity(
    amenity_id: int,
    session=TransactionSessionDep,
):
    return await HotelAmenityDAO.delete(
        session=session,
        filters=HotelAmenityFilter(
            id=amenity_id,
        ),
    )


@router.post("/categories")
async def create_hotel_amenities_category(
    hotel_amenity_category_data: HotelAmenityCategoryCreate,
    session=TransactionSessionDep,
):
    """
    Создать категорию удобств отеля
    """
    return await HotelAmenityCategoryDAO.create(
        session=session,
        values=HotelAmenityCategoryCreateInternal(
            name=hotel_amenity_category_data.to_dict_name(),
        ),
    )


@router.put(
    "/categories/{category_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def update_hotel_amenities_category(
    category_id: int,
    amenity_update_data: HotelAmenityCategoryUpdate,
    hotel_amenities_category=Depends(validate_hotel_amenities_category),
    session=TransactionSessionDep,
):
    """
    Обновить удобство в категории
    """
    return await HotelAmenityDAO.update(
        session=session,
        filters=HotelAmenityCategoryFilter(
            id=category_id,
        ),
        values=amenity_update_data,
    )


@router.delete("/categories/{category_id}")
async def delete_hotel_amenities_category(
    category_id: int,
    hotel_amenities_category=Depends(validate_hotel_amenities_category),
    session=TransactionSessionDep,
):
    """
    Удалить категорию удобств отеля
    """

    return await HotelAmenityCategoryDAO.delete(
        session=session,
        filters=HotelAmenityCategoryFilter(
            id=hotel_amenities_category.id,
        ),
    )
