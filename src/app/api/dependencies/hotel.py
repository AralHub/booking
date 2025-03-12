from fastapi import Depends
from sqlalchemy import select

from app.api.dependencies.user import get_current_auth_user
from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    UnauthorizedException,
)
from app.models.hotel import Hotel
from app.models.room import Room
from app.schemas.hotel.info import HotelNameRead
from app.schemas.user import UserRead


async def validate_active_hotel(
    hotel_id: int,
    session=SessionDep,
):
    query = select(Hotel).filter_by(id=hotel_id)
    result = await session.execute(query)
    db_hotel = result.unique().scalar_one_or_none()
    if not db_hotel:
        raise NotFoundException("Hotel not found")
    if not db_hotel.is_active:
        raise NotFoundException("Hotel is inactive")
    return db_hotel


async def validate_hotel_id(
    hotel_id: int,
    session=SessionDep,
):
    query = select(Hotel).filter_by(id=hotel_id)
    result = await session.execute(query)
    db_hotel = result.unique().scalar_one_or_none()
    if not db_hotel:
        raise NotFoundException("Hotel not found")
    return db_hotel


async def validate_hotel_room_id(
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    query = select(Room).filter_by(id=room_id, hotel_id=hotel.id)
    result = await session.execute(query)
    db_room = result.unique().scalar_one_or_none()
    if not db_room:
        raise NotFoundException("Room not found")
    return db_room


async def valid_hotel_admin(
    hotel: HotelNameRead = Depends(validate_hotel_id),
    current_user: UserRead = Depends(get_current_auth_user),
):
    if hotel.hotel_admin_id != current_user.id:
        raise UnauthorizedException("Permission denied")

    return hotel
