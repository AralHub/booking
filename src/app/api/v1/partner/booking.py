from fastapi import APIRouter, Depends

from app.api.dependencies.partner import get_current_auth_partner
from app.core import SessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.translations import ErrorCode
from app.dao.hotel import HotelDAO
from app.schemas.hotel import HotelFilter
from app.schemas.partner import (
    PartnerRead,
)
from app.dao.booking import BookingDAO
from app.schemas.booking import BookingFilter

router = APIRouter()


@router.get("/bookings")
async def get_bookings(
    partner: PartnerRead = Depends(get_current_auth_partner),
    session=SessionDep,
):
    partner_hotels = await HotelDAO.get_one_or_none(
        session=session,
        filters=HotelFilter(
            hotel_admin_id=partner.id,
        ),
    )
    if not partner_hotels:
        raise NotFoundException(
            ErrorCode.HOTEL_NOT_FOUND,
            "Hotel not found",
        )
    bookings = await BookingDAO.get_all(
        session=session,
        filters=BookingFilter(
            hotel_id=partner_hotels.id,
        ),
    )
    return bookings
