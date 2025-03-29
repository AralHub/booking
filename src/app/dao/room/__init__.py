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
import logging

logger = logging.getLogger(__name__)


class RoomTypeDAO(BaseDAO):
    model = RoomType


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def get_booked_rooms_by_hotel_id(
        cls,
        session: AsyncSession,
        check_in_date: date,
        check_out_date: date,
        hotel_id: int,
    ):
        # Получаем все активные бронирования на указанные даты
        booked_rooms_stmt = (
            select(
                BookedRoom.room_id,
            )
            .join(Booking)
            .where(
                and_(
                    Room.hotel_id == hotel_id,
                    Booking.status == BookingStatus.BOOKED,
                    or_(
                        # Scenario 1: booking starts before check-in and ends after
                        and_(
                            Booking.check_in_date <= check_in_date,
                            Booking.check_out_date > check_in_date,
                        ),
                        # Scenario 2: booking starts before check-out and ends after
                        and_(
                            Booking.check_in_date < check_out_date,
                            Booking.check_out_date >= check_out_date,
                        ),
                        # Scenario 3: booking completely within requested period
                        and_(
                            Booking.check_in_date >= check_in_date,
                            Booking.check_out_date <= check_out_date,
                        ),
                    ),
                )
            )
        )

        booked_room_ids = set(
            (await session.execute(booked_rooms_stmt)).scalars().all()
        )
        return booked_room_ids

    @classmethod
    async def check_rooms_availability(
        cls,
        session: AsyncSession,
        hotel_id: int,
        room_requests: list[BookedRoomCreate],
        check_in_date: date,
        check_out_date: date,
    ) -> bool:
        # Получаем все комнаты отеля сгруппированные по типу
        stmt = (
            select(Room.room_type_id, func.count(Room.id).label("total_rooms"))
            .where(and_(Room.hotel_id == hotel_id, Room.is_active == True))
            .group_by(Room.room_type_id)
        )

        result = await session.execute(stmt)
        rows = result.fetchall()
        logger.debug(f"Query result rows: {rows}")  # Проверим структуру результата
        available_rooms = {row.room_type_id: row.total_rooms for row in rows}
        logger.debug(f"Available rooms by type: {available_rooms}")

        # Добавим проверку конкретных комнат
        requested_room_ids = set()
        for room_request in room_requests:
            if room_request.room_id in requested_room_ids:
                raise BadRequestException("Duplicate room request")
            requested_room_ids.add(room_request.room_id)

        # Проверяем, что запрошенные комнаты не забронированы
        booked_room_ids = await cls.get_booked_rooms_by_hotel_id(
            session=session,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_id=hotel_id,
        )

        if requested_room_ids & booked_room_ids:
            raise BadRequestException("Some of the requested rooms are already booked")

        return True
