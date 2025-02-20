from fastapi import APIRouter

from app.api.locations.dao import LocationDAO
from app.api.locations.schemas import (
    LocationCreateInternal,
)

# from slugify import slugify
# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings

from .dao import HotelCategoryDAO, HotelDAO
from .schemas import (
    HotelCategoryCreate,
    HotelCategoryFilter,
    HotelCategoryUpdate,
    HotelCreate,
    HotelCreateInternal,
    HotelFilter,
    HotelUpdate,
)

router = APIRouter(
    tags=["Hotel"],
    prefix=settings.api_v1.hotel_prefix,
)


# region Hotel
@router.get("/count/")
async def get_hotels_count(
    session=SessionDep,
):
    return await HotelDAO.count(
        session=session,
        filters=None,
    )


@router.get("/")
async def get_all_hotels(
    session=SessionDep,
):
    return await HotelDAO.get_all(
        session=session,
        filters=None,
    )


@router.get("/{hotel_id}/")
async def get_hotel(
    hotel_id: int,
    session=SessionDep,
):
    return await HotelDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )


@router.post("/")
async def create_hotel(
    hotel_create_data: HotelCreate,
    session=TransactionSessionDep,
):

    created_location = await LocationDAO.create(
        session=session,
        values=LocationCreateInternal(
            **hotel_create_data.location.model_dump(),
        ),
    )
    hotel_data = HotelCreateInternal(
        **hotel_create_data.model_dump(
            exclude={"location"},
        ),
        location_id=created_location.id,
    )
    return await HotelDAO.create(
        session=session,
        values=hotel_data,
    )


@router.put("/{hotel_id}/")
async def update_hotel(
    hotel_update_data: HotelUpdate,
    hotel_id: int,
    session=TransactionSessionDep,
):
    return await HotelDAO.update(
        session=session,
        values=hotel_update_data,
        filters=HotelFilter(
            id=hotel_id,
        ),
    )


@router.delete("/{hotel_id}/")
async def delete_hotel(
    hotel_id: int,
    session=TransactionSessionDep,
):
    return await HotelDAO.delete(
        session=session,
        filters=HotelFilter(id=hotel_id),
    )


# endregion


# region Hotel Category
@router.get("/categories/")
async def get_hotel_categories(
    session=SessionDep,
):
    return await HotelCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/categories/")
async def create_hotel_category(
    hotel_category_create_data: HotelCategoryCreate,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.create(
        session=session,
        values=hotel_category_create_data,
    )


@router.put("/categories/{category_id}/")
async def update_hotel_category(
    category_update_data: HotelCategoryUpdate,
    category_id: int,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.update(
        session=session,
        values=category_update_data,
        filters=HotelCategoryFilter(id=category_id),
    )


@router.delete("/categories/{category_id}/")
async def delete_hotel_category(
    category_id: int,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.delete(
        session=session,
        filters=HotelCategoryFilter(id=category_id),
    )


# endregion
