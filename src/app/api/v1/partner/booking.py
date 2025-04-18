from fastapi import APIRouter, Depends, Query

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import get_current_auth_partner
from app.core import SessionDep, TransactionSessionDep
from app.core.i18n.responses import BaseResponse, PaginatedResponse
from app.dao.booking import BookingDAO
from app.models.booking import BookingStatus
from app.schemas.booking import BookingFilter, BookingUpdateInternal
from app.schemas.hotel.info import HotelNameRead
from app.schemas.partner import (
    PartnerRead,
)

router = APIRouter(prefix="/hotels")


@router.get("/{hotel_slug}/bookings")
async def get_bookings(
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    partner: PartnerRead = Depends(get_current_auth_partner),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    session=SessionDep,
):
    if not hotel:
        return PaginatedResponse(
            data=[],
            pagination={
                "page": page,
                "page_size": page_size,
                "total": 0,
                "total_pages": 1,
            },
        )
    bookings = await BookingDAO.get_bookings_by_hotel_id(
        session=session,
        hotel_id=hotel.id,
        page=1,
        page_size=10,
    )
    return PaginatedResponse(
        data=bookings,
        pagination={
            "page": 1,
            "page_size": 10,
            "total": len(bookings),
            "total_pages": 1,
        },
    )


@router.put("/{hotel_slug}/bookings/{booking_id}/complete")
async def complete_booking(
    booking_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    partner: PartnerRead = Depends(get_current_auth_partner),
    session=TransactionSessionDep,
):
    await BookingDAO.update(
        session=session,
        filters=BookingFilter(
            id=booking_id,
            hotel_id=hotel.id,
        ),
        values=BookingUpdateInternal(
            status=BookingStatus.COMPLETED,
        ),
    )
    return BaseResponse(
        success=True,
        message="Бронь завершена",
    )
