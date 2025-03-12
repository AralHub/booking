import logging

from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import valid_hotel_admin, validate_hotel_id
from app.core import TransactionSessionDep
from app.dao.hotel import HotelInfoDAO
from app.schemas.hotel.info import (
    HotelInfoCreate,
    HotelInfoCreateInternal,
    HotelInfoFilter,
    HotelInfoUpdate,
    HotelInfoUpdateInternal,
    HotelNameRead,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotel Info"],
)


@router.get("/{hotel_id}/info")
async def get_hotel_info(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):
    return await HotelInfoDAO.get_hotel_info(
        session=session,
        hotel_id=hotel_id,
    )


@router.post("/{hotel_id}/info")
async def add_hotel_info(
    hotel_id: int,
    hotel_info_create_data: HotelInfoCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):

    return await HotelInfoDAO.create(
        session=session,
        values=HotelInfoCreateInternal(
            **hotel_info_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


@router.put("/{hotel_id}/info")
async def update_hotel_info(
    hotel_id: int,
    hotel_info_update_data: HotelInfoUpdate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    return await HotelInfoDAO.update(
        session=session,
        values=HotelInfoUpdateInternal(
            **hotel_info_update_data.model_dump(),
            hotel_id=hotel_id,
        ),
        filters=HotelInfoFilter(
            hotel_id=hotel_id,
        ),
    )
