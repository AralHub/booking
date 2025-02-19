from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings

from .dao import AmenityCategoryDAO, AmenityDAO
from .schemas import (
    AmenityCategoryCreate,
    AmenityCreate,
)

router = APIRouter(
    prefix=settings.api_v1.amenity_prefix,
)
# router = APIRouter(
#     tags=["Amenity"],
#     prefix=settings.api_v1.amenity_prefix,
# )


@router.get("/")
async def get_amenities(
    session=SessionDep,
):
    return await AmenityDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/")
async def create_amenity(
    amenity_create_data: AmenityCreate,
    session=TransactionSessionDep,
):
    return await AmenityDAO.create(
        session=session,
        values=amenity_create_data,
    )


@router.get("/categories/")
async def get_amenity_categories(
    session=SessionDep,
):
    return await AmenityCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/categories/")
async def create_amenity_category(
    amenity_category_create_data: AmenityCategoryCreate,
    session=TransactionSessionDep,
):
    return await AmenityCategoryDAO.create(
        session=session,
        values=amenity_category_create_data,
    )
