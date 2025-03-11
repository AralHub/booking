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
)
from app.schemas.partner import PartnerRead

from .images import router as images_router

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotels"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get("/search")
async def search_hotels(
    city_id: int = Query(..., description="ID города"),
    check_in: str = Query(..., description="Дата заезда"),
    check_out: str = Query(..., description="Дата выезда"),
    guests: str = Query(
        ..., description="Количество гостей по комнатам, например: 3-1 для 2 комнат"
    ),
    session=SessionDep,
):
    parsed_check_in = parse_date(check_in)
    parsed_check_out = parse_date(check_out)
    return await HotelDAO.find_hotels(
        session=session,
        city_id=city_id,
        check_in_date=parsed_check_in,
        check_out_date=parsed_check_out,
        guests=guests,
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


router.include_router(images_router)
