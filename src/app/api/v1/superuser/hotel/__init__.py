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
from app.schemas.user import UserRead

router = APIRouter(
    tags=["Superuser Hotels"],
    prefix="/superuser/hotels",
)


@router.get("")
async def get_hotels(
    superuser: UserRead = Depends(get_current_superuser),
    session=SessionDep,
):
    all_hotels = await HotelDAO.get_all_hotels_for_superuser(
        session=session,
    )
    return {
        "data": all_hotels,
        "total": len(all_hotels),
    }


@router.put("/{hotel_id}/change-status")
async def update_hotel(
    hotel_id: int,
    status: BookingStatus,
    superuser: UserRead = Depends(get_current_superuser),
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
