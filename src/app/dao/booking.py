from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.http_exceptions import BadRequestException, NotFoundException
from app.dao import BaseDAO
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO
from app.dao.user import UserDAO
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User

from app.models.booking import Booking, BookingStatus
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingCreateMultipleRoomsInternal,
)


class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    async def create_booking(
        cls,
        session: AsyncSession,
        booking_data: BookingCreateMultipleRooms,
        user_id: int,
    ):
        # Проверка корректности дат
        if booking_data.check_in_date >= booking_data.check_out_date:
            raise BadRequestException("Check-out date must be after check-in date")

        # Проверка существования пользователя
        db_user = await UserDAO.get_one_or_none_by_id(
            session=session,
            data_id=user_id,
        )
        if not db_user:
            raise NotFoundException("User not found")
        db_room = await RoomDAO.get_one_or_none_by_id(
            session=session,
            data_id=booking_data.room_id,
        )
        if not db_room:
            raise NotFoundException("Room not found")
        # Подсчет пересекающихся активных бронирований для номера
        overlapping_bookings = await session.execute(
            select(func.count(Booking.id)).where(
                Booking.room_id == booking_data.room_id,
                Booking.status != BookingStatus.CANCELLED,
                Booking.check_out_date > booking_data.check_in_date,
                Booking.check_in_date < booking_data.check_out_date,
            )
        )
        overlapping_count = overlapping_bookings.scalar_one()

        # Получение общего количества номеров данного типа
        room_quantity = await session.execute(
            select(Room.quantity).where(Room.id == booking_data.room_id)
        )
        quantity = room_quantity.scalar_one()

        # Проверка доступности номера
        if overlapping_count >= quantity:
            raise BadRequestException("No available rooms for the selected period")

        # Вычисление количества дней и общей стоимости
        total_days = (booking_data.check_out_date - booking_data.check_in_date).days
        if db_room.use_dinamic_price:
            room_price = await RoomPriceDAO.get_room_price(
                session=session,
                room_id=booking_data.room_id,
                guest_quantity=booking_data.guest_quantity,
            )
            total_price = total_days * room_price
        else:
            total_price = total_days * db_room.base_price

        # Создание бронирования
        return await cls.create(
            session=session,
            values=BookingCreateInternal(
                **booking_data.model_dump(),
                total_days=total_days,
                total_price=total_price,
                user_id=user_id,
            ),
        )
