import logging

from fastapi import APIRouter, Depends, Query

from app.api.dependencies.hotel import validate_hotel, validate_hotel_by_slug
from app.api.dependencies.partner import (
    get_current_active_auth_partner,
    valid_hotel_admin_by_slug,
)
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.translations import ErrorCode
from app.dao.hotel import HotelDAO
from app.schemas.hotel import (
    HotelFullCreate,
    HotelFullUpdate,
    HotelSearch,
    HotelSearchResult,
)
from app.schemas.hotel.info import HotelNameRead
from app.schemas.partner import PartnerRead
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    DataResponse,
    ListResponse,
    PaginatedResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotels"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get("/count")
async def get_hotels_count(
    session=SessionDep,
):
    return await HotelDAO.count(
        session=session,
    )


@router.get("/popular")
async def get_popular_hotels(
    limit: int = Query(default=10, ge=1, le=100),
    session=SessionDep,
):
    return await HotelDAO.get_popular_hotels(
        session=session,
        limit=limit,
    )


@router.post(
    "/search",
    response_model=PaginatedResponse[HotelSearchResult],
)
async def search_hotels(
    search_data: HotelSearch,
    session=SessionDep,
):
    hotels = await HotelDAO.find_hotels_for_booking(
        session=session,
        city=search_data.city,
        check_in_date=search_data.check_in,
        check_out_date=search_data.check_out,
        guests=search_data.guests,
        price_min=search_data.price_min,
        price_max=search_data.price_max,
        max_distance_to_center=search_data.max_distance_to_center,
        amenities=search_data.amenities,
    )
    if not hotels:
        return PaginatedResponse(
            data=[],
            paginate={
                "page": 1,
                "page_size": 10,
                "total": 0,
                "total_pages": 1,
            },
        )
    return PaginatedResponse(
        data=[HotelSearchResult.model_validate(hotel) for hotel in hotels],
        paginate={
            "page": 1,
            "page_size": 10,
            "total": len(hotels),
            "total_pages": 1,
        },
    )


@router.get("/{hotel_slug}")
async def get_full_hotel(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    return await HotelDAO.get_full_hotel_by_id(
        session=session,
        hotel_id=hotel.id,
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


@router.put("/{hotel_slug}")
async def update_hotel(
    hotel_update_data: HotelFullUpdate,
    hotel_slug: str,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    return await HotelDAO.update_hotel(
        session=session,
        hotel_update_data=hotel_update_data,
        hotel_id=hotel.id,
    )
