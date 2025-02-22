from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep

from .dao import (
    HotelAmenityCategoryDAO,
    HotelAmenityDAO,
    RoomAmenityDAO,
)
from .schemas import (
    HotelAmenityCategoryCreate,
    HotelAmenityCreate,
    HotelAmenityFilter,
    HotelAmenityUpdate,
)

router = APIRouter(
    tags=["Amenities"],
)


@router.get("/hotel/amenity/categories/")
async def get_all_hotel_amenity_categories(
    session=SessionDep,
):
    return await HotelAmenityCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.get("/hotel/amenity/categories/{category_id}/amenities/")
async def get_hotel_amenities_by_category(
    category_id: int,
    session=SessionDep,
):
    return await HotelAmenityDAO.get_all(
        session=session,
        filters=HotelAmenityFilter(hotel_amenity_category_id=category_id),
    )


@router.get("/hotel/amenities/")
async def get_all_hotel_amenities(
    session=SessionDep,
):
    return await HotelAmenityDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/hotel/amenities/")
async def create_hotel_amenity(
    amenity_create_data: HotelAmenityCreate,
    session=TransactionSessionDep,
):
    return await HotelAmenityDAO.create(
        session=session,
        values=amenity_create_data,
    )


@router.patch("/hotel/amenities/{amenity_id}")
async def update_hotel_amenity(
    amenity_id: int,
    amenity_update_data: HotelAmenityUpdate,
    session=TransactionSessionDep,
):
    return await HotelAmenityDAO.update(
        session=session,
        filters=HotelAmenityFilter(id=amenity_id),
        values=amenity_update_data,
    )


@router.get("/hotel/amenity/categories/")
async def get_hotel_amenity_categories(
    session=SessionDep,
):
    return await HotelAmenityCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/hotel/amenity/categories/")
async def create_hotel_amenity_category(
    amenity_category_create_data: HotelAmenityCategoryCreate,
    session=TransactionSessionDep,
):
    return await HotelAmenityCategoryDAO.create(
        session=session,
        values=amenity_category_create_data,
    )


@router.get("/room/amenities/")
async def get_all_room_amenities(
    session=SessionDep,
):
    return await RoomAmenityDAO.get_all(
        session=session,
        filters=None,
    )
