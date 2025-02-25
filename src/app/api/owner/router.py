from datetime import UTC, datetime

# from app.core.config import settings
from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.api.hotel.dao import HotelDAO
from .dao import HotelOwnerDAO, HotelOwnerInfoDAO
from .schemas import (
    HotelOwnerInfoCreate,
    HotelOwnerInfoCreateInternal,
    HotelOwnerInfoFilter,
    HotelOwnerInfoRead,
)

router = APIRouter(
    tags=["Hotel Owner"],
)


# region Hotel Owner
@router.get("/hotels/{hotel_id}/owner")
async def get_hotel_owner(
    hotel_id: int,
    session=SessionDep,
):
    db_hotel_owner = await HotelOwnerDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )
    if not db_hotel_owner:
        raise NotFoundException("Hotel owner not found")
    return db_hotel_owner


# endregion


# region OwnerInfo
@router.get(
    "/hotels/{hotel_id}/owner/info",
    response_model=HotelOwnerInfoRead,
)
async def get_hotel_owner_info(
    hotel_id: int,
    session=TransactionSessionDep,
):
    db_hotel = await HotelDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )
    if not db_hotel:
        raise NotFoundException("Hotel not found")
    return await HotelOwnerInfoDAO.get_one_or_none(
        session=session,
        filters=HotelOwnerInfoFilter(hotel_id=hotel_id),
    )


@router.post("/hotels/{hotel_id}/owner/info")
async def add_hotel_owner_info(
    hotel_id: int,
    hotel_owner_info_create_data: HotelOwnerInfoCreate,
    session=TransactionSessionDep,
):
    db_hotel = await HotelDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )
    if not db_hotel:
        raise NotFoundException("Hotel not found")

    return await HotelOwnerInfoDAO.create(
        session=session,
        values=HotelOwnerInfoCreateInternal(
            **hotel_owner_info_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


# endregion
