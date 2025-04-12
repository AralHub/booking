from fastapi import APIRouter, Depends

from app.api.dependencies.partner import get_current_auth_partner
from app.core import SessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.translations import ErrorCode
from app.dao.hotel import HotelDAO
from app.schemas.hotel.info import HotelInfoFilter
from app.schemas.partner import (
    PartnerRead,
)

router = APIRouter(
    tags=["Partners"],
    prefix="/partners",
)


@router.get("/hotels")
async def get_hotels(
    partner: PartnerRead = Depends(get_current_auth_partner),
    session=SessionDep,
):
    partner_hotels = await HotelDAO.get_one_or_none(
        session=session,
        filters=HotelInfoFilter(
            hotel_admin_id=partner.id,
        ),
    )
    if not partner_hotels:
        raise NotFoundException(
            ErrorCode.HOTEL_NOT_FOUND,
            "Hotel not found",
        )
    hotel = await HotelDAO.get_full_hotel_by_id(
        session=session,
        hotel_id=partner_hotels.id,
    )
    if not hotel:
        raise NotFoundException(
            ErrorCode.HOTEL_NOT_FOUND,
            "Hotel not found",
        )
    return {
        "data": hotel,
    }
