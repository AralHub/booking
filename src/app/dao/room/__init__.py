from datetime import date
from sqlalchemy import and_, func, or_, select, case, text, literal_column, table
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    BadRequestException,
)
from app.dao import BaseDAO
from app.models.booking import Booking, BookingStatus
from app.dao.room.price import RoomPriceDAO
from app.models.room import Room
from app.models.room.price import RoomPrice
from app.models.room.types import RoomType
from app.models.booking import BookedRoom
from app.schemas.booking import BookedRoomCreate
from app.schemas.room import (
    RoomCreateInternal,
    RoomCreate,
    RoomUpdate,
    RoomUpdateInternal,
    RoomFilter,
)
from app.schemas.room.types import RoomTypeFilter
import logging

logger = logging.getLogger(__name__)


class RoomTypeDAO(BaseDAO):
    model = RoomType


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def add_room_to_hotel(
        cls,
        session: AsyncSession,
        room_data: RoomCreate,
        hotel_id: int,
    ):
        db_room_type = await RoomTypeDAO.get_one_or_none(
            session=session,
            filters=RoomTypeFilter(
                id=room_data.room_type_id,
            ),
        )
        if not db_room_type:
            raise NotFoundException(
                detail="Room type not found",
            )
        hotel_room_create_data = RoomCreateInternal(
            **room_data.model_dump(),
            hotel_id=hotel_id,
        )
        return await cls.create(
            session=session,
            values=hotel_room_create_data,
        )

    @classmethod
    async def update_hotel_room(
        cls,
        session: AsyncSession,
        room_data: RoomUpdate,
        room_id: int,
        hotel_id: int,
    ):
        # Проверяем существование room_type если он указан
        if room_data.room_type_id is not None:
            room_type = await RoomTypeDAO.get_one_or_none(
                session=session,
                filters=RoomTypeFilter(
                    id=room_data.room_type_id,
                ),
            )
            if not room_type:
                raise NotFoundException("Room type does not exist")
        updated_row_count = await RoomDAO.update(
            session=session,
            values=RoomUpdateInternal(
                **room_data.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                )
            ),
            filters=RoomFilter(
                id=room_id,
                hotel_id=hotel_id,
            ),
        )
        if updated_row_count == 0 or updated_row_count is None:
            raise NotFoundException("Room did not update")
        return {
            "message": "Room updated successfully",
        }

    