from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
    ListResponse,
)
from app.dao.hotel import HotelDAO
from app.models.booking import BookingStatus
from app.schemas.hotel.info import (
    HotelNameFilter,
    HotelNameRead,
    HotelNameUpdateInternal,
)

router = APIRouter(
    tags=["Superuser Hotels"],
    prefix="/superuser/hotels",
)


@router.get("")
async def get_hotels(
    session=SessionDep,
):
    hotels = await HotelDAO.get_all(
        session=session,
        filters=None,
    )
    return {
        "data": hotels,
        "total": len(hotels),
    }


@router.put("/{hotel_id}/activate")
async def update_hotel(
    hotel_id: int,
    status: BookingStatus,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=TransactionSessionDep,
):
    await HotelDAO.update(
        session=session,
        values=HotelNameUpdateInternal(
            is_active=not hotel.is_active,
        ),
        filters=HotelNameFilter(
            id=hotel_id,
        ),
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.DATA_UPDATED,
    )
