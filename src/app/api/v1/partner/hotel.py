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

router = APIRouter(prefix="/hotels")


@router.get("")
async def get_hotels(
    partner: PartnerRead = Depends(get_current_auth_partner),
    session=SessionDep,
):
    partner_hotels = await HotelDAO.get_hotels_by_partner_id(
        session=session,
        partner_id=partner.id,
    )
    return {
        "data": partner_hotels,
        "total": len(partner_hotels),
    }


@router.get("/{hotel_slug}")
async def get_hotel(
    hotel_slug: str,
    partner: PartnerRead = Depends(get_current_auth_partner),
    session=SessionDep,
):
    partner_hotels = await HotelDAO.get_one_or_none(
        session=session,
        filters=HotelFilter(
            hotel_admin_id=partner.id,
            slug=hotel_slug,
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
        return {
            "data": {},
        }
    return {
        "data": hotel,
    }
