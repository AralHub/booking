import logging

from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import get_current_active_auth_partner
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.translations import ErrorCode
from app.dao.hotel import HotelDAO
from app.schemas.hotel import (
    HotelFullCreate,
    HotelFullUpdate,
    HotelSearch,
)
from app.schemas.hotel.info import HotelNameRead
from app.schemas.partner import PartnerRead

from .amenities import router as amenities_router
from .images import router as images_router
from .info import router as info_router
from .location import router as location_router
from .review import router as review_router
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
    hotels = await HotelDAO.find_hotels_for_booking(
        session=session,
        city_id=search_data.city_id,
        check_in_date=search_data.check_in,
        check_out_date=search_data.check_out,
        guests=search_data.guests,
    )
    if not hotels:
        return []
    return hotels


@router.get("/{hotel_id}")
async def get_full_hotel(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    return await HotelDAO.get_full_hotel_by_id(
        session=session,
        hotel_id=hotel_id,
    )


@router.post("")
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
router.include_router(rules_router)
router.include_router(amenities_router)
router.include_router(images_router)
router.include_router(review_router)
