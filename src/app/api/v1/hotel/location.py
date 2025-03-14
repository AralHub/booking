from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import valid_hotel_admin, validate_hotel_id
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.dao.hotel import HotelDAO
from app.dao.hotel.location import HotelLocationDAO
from app.schemas.hotel.info import HotelNameFilter, HotelNameRead
from app.schemas.hotel.location import (
    LocationCreate,
    LocationFilter,
    LocationUpdate,
    LocationUpdateInternal,
)

router = APIRouter(
    tags=["Hotel Location"],
)


@router.get("/location/{city_id}")
async def get_hotels_by_city_id(
    city_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    db_hotels = await HotelDAO.get_all(
        session=session,
        filters=HotelNameFilter(
            city_id=city_id,
        ),
    )
    return db_hotels


@router.get("/{hotel_id}/location")
async def get_hotel_location(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
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
    return await HotelLocationDAO.update(
        session=session,
        values=LocationUpdateInternal(
            **location_update_data.model_dump(
                exclude_none=True,
                exclude_unset=True,
            ),
        ),
        filters=LocationFilter(
            hotel_id=hotel_id,
        ),
    )
