from fastapi import Depends

from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)

from .dao import HotelDAO
from .schemas import HotelNameBase


async def validate_active_hotel(
    hotel_id: int,
    session=SessionDep,
):
    db_hotel = await HotelDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )
    if not db_hotel:
        raise NotFoundException("Hotel not found")
    if not db_hotel.is_active:
        raise NotFoundException("Hotel is inactive")
    return db_hotel


async def validate_hotel_id(
    hotel_id: int,
    session=SessionDep,
):
    db_hotel = await HotelDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )
    if not db_hotel:
        raise NotFoundException("Hotel not found")
    return db_hotel


async def validate_hotel_room_id(
    room_id: int,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=SessionDep,
):
    pass
