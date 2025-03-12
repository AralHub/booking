import logging

from fastapi import APIRouter, Depends, Query

from app.api.dependencies.hotel import validate_hotel_id
from app.api.dependencies.partner import get_current_active_auth_partner
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.utils.parse_date import parse_date
from app.dao.hotel import HotelDAO
from app.schemas.hotel import (
    HotelFullCreate,
    HotelFullUpdate,
    HotelSearch,
)
from app.schemas.partner import PartnerRead

from .amenities import router as amenities_router
from .images import router as images_router
from .info import router as info_router
from .location import router as location_router
from .rules import router as rules_router

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotels"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.post("/search")
async def search_hotels(
    search_data: HotelSearch,
    session=SessionDep,
):
    parsed_check_in = parse_date(search_data.check_in)
    parsed_check_out = parse_date(search_data.check_out)
    return await HotelDAO.find_hotels_for_booking(
        session=session,
        city_id=search_data.city_id,
        check_in_date=parsed_check_in,
        check_out_date=parsed_check_out,
        guests=search_data.guests,
    )


@router.post("/")
async def create_hotel(
    hotel_create_data: HotelFullCreate,
    partner: PartnerRead = Depends(get_current_active_auth_partner),
    session=TransactionSessionDep,
):
    return await HotelDAO.create_new_hotel(
        session=session,
        hotel_create_data=hotel_create_data,
        hotel_admin_id=partner.id,
    )


@router.put("/{hotel_id}")
async def update_hotel(
    hotel_update_data: HotelFullUpdate,
    hotel_id: int,
    partner: PartnerRead = Depends(get_current_active_auth_partner),
    session=TransactionSessionDep,
):
    return await HotelDAO.update_hotel(
        session=session,
        hotel_update_data=hotel_update_data,
        hotel_id=hotel_id,
    )


router.include_router(location_router)
router.include_router(info_router)
router.include_router(images_router)
router.include_router(rules_router)
router.include_router(amenities_router)
