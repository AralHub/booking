from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import NotFoundException
from app.dao.hotel.location import HotelLocationDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.hotel.location import (
    LocationCreate,
    LocationFilter,
    LocationUpdate,
)

router = APIRouter(
    tags=["Hotel Location"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get("/{hotel_id}/location")
async def get_hotel_location(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    db_hotel_location = await HotelLocationDAO.get_one_or_none(
        session=session,
        filters=LocationFilter(
            hotel_id=hotel_id,
        ),
    )
    if not db_hotel_location:
        raise NotFoundException("Hotel location not found")
    return db_hotel_location


@router.post("/{hotel_id}/location")
async def add_hotel_location(
    hotel_id: int,
    location_create_data: LocationCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    return await HotelLocationDAO.add_hotel_location(
        session=session,
        location_create_data=location_create_data,
        hotel_id=hotel_id,
    )


@router.put("/{hotel_id}/location")
async def update_hotel_location(
    hotel_id: int,
    location_update_data: LocationUpdate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    return await HotelLocationDAO.update_hotel_location(
        session=session,
        location_update_data=location_update_data,
        hotel_id=hotel_id,
    )
