from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import get_current_auth_partner
from app.core import SessionDep
from app.dao.booking import BookingDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.partner import (
    PartnerRead,
)

router = APIRouter(prefix="/hotels")


@router.get("/{hotel_slug}/bookings")
async def get_bookings(
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    partner: PartnerRead = Depends(get_current_auth_partner),
    session=SessionDep,
):
    if not hotel:
        return {
            "data": [],
            "total": 0,
        }
    bookings = await BookingDAO.get_bookings_by_hotel_id(
        session=session,
        hotel_id=hotel.id,
    )
    return {
        "data": bookings,
        "total": len(bookings),
    }
