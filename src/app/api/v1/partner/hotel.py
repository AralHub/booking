from fastapi import APIRouter, Depends

from app.api.dependencies.partner import (
    get_current_auth_partner,
    valid_hotel_admin_by_slug,
)
from app.core import SessionDep
from app.dao.hotel import HotelDAO
from app.schemas.hotel.info import HotelNameRead
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
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=SessionDep,
):
    if not hotel:
        return {
            "data": {},
        }
    hotel = await HotelDAO.get_full_hotel_by_id(
        session=session,
        hotel_id=hotel.id,
    )
    if not hotel:
        return {
            "data": {},
        }
    return {
        "data": hotel,
    }
