import logging

from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel, validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin, valid_hotel_admin_by_slug
from app.core import TransactionSessionDep
from app.core.config import settings
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    DataResponse,
)
from app.dao.hotel import HotelInfoDAO
from app.schemas.hotel.info import (
    HotelInfoCreate,
    HotelInfoCreateInternal,
    HotelInfoFilter,
    HotelInfoRead,
    HotelInfoUpdate,
    HotelInfoUpdateInternal,
    HotelNameRead,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotel Infos"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get(
    "/{hotel_slug}/info",
    response_model=DataResponse[HotelInfoRead],
)
async def get_hotel_info(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=TransactionSessionDep,
):
    hotel_info = await HotelInfoDAO.get_hotel_info(
        session=session,
        hotel_id=hotel.id,
    )
    return DataResponse[HotelInfoRead](
        data=hotel_info,
    )


@router.post(
    "/{hotel_slug}/info",
    response_model=DataResponse[HotelInfoRead],
)
async def add_hotel_info(
    hotel_slug: str,
    hotel_info_create_data: HotelInfoCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):

    created_hotel_info = await HotelInfoDAO.create(
        session=session,
        values=HotelInfoCreateInternal(
            **hotel_info_create_data.model_dump(),
            hotel_id=hotel.id,
        ),
    )
    return DataResponse[HotelInfoRead](
        data=created_hotel_info,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Hotel info added successfully",
        ),
    )


@router.put(
    "/{hotel_slug}/info",
    response_model=DataResponse[HotelInfoRead],
)
async def update_hotel_info(
    hotel_slug: str,
    hotel_info_update_data: HotelInfoUpdate,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    updated_hotel_info = await HotelInfoDAO.update(
        session=session,
        values=HotelInfoUpdateInternal(
            **hotel_info_update_data.model_dump(),
            hotel_id=hotel.id,
        ),
        filters=HotelInfoFilter(
            hotel_id=hotel.id,
        ),
    )
    return DataResponse[HotelInfoRead](
        data=updated_hotel_info,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "Hotel info updated successfully",
        ),
    )
