import logging

from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
from app.core.i18n.responses import (
    DataResponse,
    BaseResponse,
    RESPONSE_MESSAGES,
    ListResponse,
)
from app.core import TransactionSessionDep
from app.core.config import settings
from app.dao.hotel import HotelInfoDAO
from app.schemas.hotel.info import (
    HotelInfoCreate,
    HotelInfoCreateInternal,
    HotelInfoFilter,
    HotelInfoUpdate,
    HotelInfoUpdateInternal,
    HotelNameRead,
    HotelInfoRead,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotel Infos"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get(
    "/{hotel_id}/info",
    response_model=DataResponse[HotelInfoRead],
)
async def get_hotel_info(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=TransactionSessionDep,
):
    hotel_info = await HotelInfoDAO.get_hotel_info(
        session=session,
        hotel_id=hotel_id,
    )
    return DataResponse[HotelInfoRead](
        data=hotel_info,
        message=RESPONSE_MESSAGES.get(
            "DATA_RETRIEVED",
            "Hotel info retrieved successfully",
        ),
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
