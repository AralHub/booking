from sqlalchemy.ext.asyncio import AsyncSession

from app.api.booking.models import Booking
from app.api.user.dao import UserDAO
from app.core.dao import BaseDAO
from app.core.exceptions.http_exceptions import BadRequestException, NotFoundException

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
                total_price=total_days * 100,
                user_id=user_id,
            ),
        )
