from datetime import date
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.core.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException

from app.api.user.dao import UserDAO
from app.core.dao import BaseDAO
from app.core.exceptions.http_exceptions import BadRequestException, NotFoundException

from .models import Booking, BookingStatus
from .schemas import BookingCreate, BookingCreateInternal


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
        Проверяется путем подсчета кол-ва букингов задевающих этот период и
        Вычитанием этого кол-ва из кол-ва Доступных номеров.
        """
        if booking_data.check_in_date >= booking_data.check_out_date:
            raise BadRequestException("Check-out date must be after check-in date")
        db_user = await UserDAO.get_one_or_none_by_id(
            session=session,
            data_id=user_id,
        )
        if not db_user:
            raise NotFoundException("User not found")
        total_days = (booking_data.check_out_date - booking_data.check_in_date).days
        return await cls.create(
            session=session,
            values=BookingCreateInternal(
                **booking_data.model_dump(),
                total_days=total_days,
                total_price=total_days,
                user_id=user_id,
            ),
        )

    @classmethod
    async def get_booked_room(
        cls,
        session: AsyncSession,
        check_in: date,
        check_out: date,
        room_id: int,
    ):
        booked_room_query = select(Booking).where(
            and_(
                Booking.room_id == room_id,
                or_(
                    and_(
                        Booking.check_in_date >= check_in,
                        Booking.check_in_date <= check_out,
                    ),
                    and_(
                        Booking.check_in_date <= check_in,
                        Booking.check_out_date > check_in,
                    ),
                ),
            )
        )
        return (await session.execute(booked_room_query)).scalars().all()
