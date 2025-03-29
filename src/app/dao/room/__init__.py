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
        # Получаем все комнаты отеля
        stmt = select(Room.id, Room.room_type_id, Room.quantity).where(
            and_(
                Room.hotel_id == hotel_id,
            )
        )
        result = await session.execute(stmt)
        rooms = result.fetchall()
        # Создаем словарь доступных комнат по их ID
        available_rooms = {room.id: room.quantity for room in rooms}

        # Проверяем запросы на комнаты
        requested_rooms = {}
        for room_request in room_requests:
            if room_request.room_id not in available_rooms:
                raise NotFoundException(f"Room {room_request.room_id} not found")

            current_quantity = requested_rooms.get(room_request.room_id, 0)
            new_quantity = current_quantity + room_request.quantity

            if new_quantity > available_rooms[room_request.room_id]:
                raise BadRequestException(
                    f"Requested quantity {new_quantity} exceeds available quantity {available_rooms[room_request.room_id]} for room {room_request.room_id}"
                )

            requested_rooms[room_request.room_id] = new_quantity

        # Проверяем, что запрошенные комнаты не забронированы
        booked_room_ids = await cls.get_booked_rooms_by_hotel_id(
            session=session,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_id=hotel_id,
        )
        # Проверяем пересечение с уже забронированными комнатами
        if set(requested_rooms.keys()) & booked_room_ids:
            raise BadRequestException("Some of the requested rooms are already booked")

        return True
