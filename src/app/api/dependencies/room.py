from fastapi import Depends
from sqlalchemy import select

from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    room_not_found,
)
from app.core.logger import logging
from app.models.room import Room
from app.schemas.hotel.info import HotelNameRead

from .hotel import validate_hotel_id

logger = logging.getLogger(__name__)


async def validate_hotel_room_id(
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    query = select(Room).filter_by(id=room_id, hotel_id=hotel.id)
    result = await session.execute(query)
    db_room = result.unique().scalar_one_or_none()
    if not db_room:
        raise room_not_found()
    return db_room
