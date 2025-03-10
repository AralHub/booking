from fastapi import Depends
from sqlalchemy import select

from app.api.user.dependencies import get_current_auth_user
from app.api.user.schemas import UserRead
from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    UnauthorizedException,
)

from .models import Hotel
from .schemas import HotelNameBase


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
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=SessionDep,
):
    pass


async def valid_hotel_admin(
    hotel: HotelNameBase = Depends(validate_hotel_id),
    current_user: UserRead = Depends(get_current_auth_user),
):
    if hotel.admin_id != current_user.id:
        raise UnauthorizedException("Permission denied")

    return hotel
