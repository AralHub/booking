from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import BaseDAO
from app.dao.room import RoomDAO
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User

from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate, BookingCreateInternal


class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    async def create_booking(
        cls,
        session: AsyncSession,
        booking_data: BookingCreate,
        user_id: int,
    ):
        """
        Создание и добавление Букинга в Бд

        В функции проверяется наличие номера на период, указанный пользователем.
        Проверяется путем подсчета кол-ва букингов, пересекающихся с этим периодом,
        и сравнения с количеством доступных номеров.
        """

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
        room_price = await RoomDAO.get_room_price(
            session=session,
            room_id=booking_data.room_id,
        )
        total_price = total_days * room_price

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
