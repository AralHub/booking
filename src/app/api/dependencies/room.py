from fastapi import Depends
from sqlalchemy import select

from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    room_not_found,
)
from app.core.i18n.translations import ErrorCode
from app.core.logger import logging
from app.models.room import Room
from app.models.room.types import RoomType
from app.schemas.hotel.info import HotelNameRead

from .hotel import validate_hotel, validate_hotel_by_slug

logger = logging.getLogger(__name__)


async def validate_hotel_room(
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    query = select(Room).filter_by(id=room_id, hotel_id=hotel.id)
    result = await session.execute(query)
    db_room = result.unique().scalar_one_or_none()
    if not db_room:
        raise room_not_found()
    return db_room


async def validate_room_type_id(
    room_type_id: int,
    session=SessionDep,
):
    query = select(RoomType).filter_by(id=room_type_id)
    result = await session.execute(query)
    db_room_type = result.unique().scalar_one_or_none()
    if not db_room_type:
        raise NotFoundException(error_code=ErrorCode.NOT_FOUND)
    return db_room_type


async def validate_hotel_room_by_slug(
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    query = select(Room).filter_by(id=room_id, hotel_id=hotel.id)
    result = await session.execute(query)
    db_room = result.unique().scalar_one_or_none()
    if not db_room:
        raise room_not_found()
    return db_room
