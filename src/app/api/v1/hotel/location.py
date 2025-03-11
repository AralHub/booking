from fastapi import APIRouter

from app.api.hotel.dao import HotelDAO
from app.api.hotel.schemas import HotelNameFilter
from app.api.location.dao import LocationDAO
from app.api.location.schemas import (
    LocationCreate,
    LocationCreateInternal,
    LocationFilter,
    LocationUpdate,
    LocationUpdateInternal,
)
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException

router = APIRouter(
    tags=["Locations"],
    prefix="/hotels",
)


@router.get("/location/{city_id}")
async def get_hotels_by_city_id(
    city_id: int,
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
    session=SessionDep,
):
    db_hotel_location = await LocationDAO.get_one_or_none(
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
    session=TransactionSessionDep,
):
    return await LocationDAO.add_hotel_location(
        session=session,
        values=LocationCreateInternal(
            **location_create_data.model_dump(
                exclude_none=True,
                excluce_unset=True,
            ),
            hotel_id=hotel_id,
        ),
    )


@router.put("/{hotel_id}/location")
async def update_hotel_location(
    hotel_id: int,
    location_update_data: LocationUpdate,
    session=TransactionSessionDep,
):
    return await LocationDAO.update(
        session=session,
        values=LocationUpdateInternal(
            **location_update_data.model_dump(),
        ),
        filters=LocationFilter(
            hotel_id=hotel_id,
        ),
    )
