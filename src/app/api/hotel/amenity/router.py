from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings

from .dao import HotelAmenityCategoryDAO, HotelAmenityDAO
from .schemas import (
    AmenityCategoryCreate,
    AmenityCreate,
    AmenityFilter,
    AmenityUpdate,
)

router = APIRouter(
    tags=["Amenity"],
    prefix=settings.api_v1.amenity_prefix,
)


@router.get("/")
async def get_amenities(
    session=SessionDep,
):
    return await HotelAmenityDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/")
async def create_amenity(
    amenity_create_data: AmenityCreate,
    session=TransactionSessionDep,
):
    return await HotelAmenityDAO.create(
        session=session,
        values=amenity_create_data,
    )


@router.patch("/{amenity_id}")
async def update_amenity(
    amenity_id: int,
    amenity_update_data: AmenityUpdate,
    session=TransactionSessionDep,
):
    return await HotelAmenityDAO.update(
        session=session,
        filters=AmenityFilter(id=amenity_id),
        values=amenity_update_data,
    )


@router.get("/categories/")
async def get_amenity_categories(
    session=SessionDep,
):
    return await HotelAmenityCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/categories/")
async def create_amenity_category(
    amenity_category_create_data: AmenityCategoryCreate,
    session=TransactionSessionDep,
):
    return await HotelAmenityCategoryDAO.create(
        session=session,
        values=amenity_category_create_data,
    )
