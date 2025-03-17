from datetime import date

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.booking import Booking, BookingStatus


from app.models.room import Room
from app.models.room.price import RoomPrice
from app.models.room.types import RoomType


class RoomTypeDAO(BaseDAO):
    model = RoomType


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def get_available_rooms(
        cls,
        session: AsyncSession,
        hotel_id: int,
        check_in_date: date,
        check_out_date: date,
        guests: int,
    ):
        booked_rooms_subquery = (
            select(Booking.room_id)
            .where(
                and_(
                    # Проверяем только активные брони (не отмененные)
                    Booking.status != BookingStatus.CANCELLED,
                    # Проверяем все возможные пересечения дат через OR
                    or_(
                        # Сценарий 1: бронь начинается до check_in и заканчивается после
                        and_(
                            Booking.check_in_date <= check_in_date,
                            Booking.check_out_date > check_in_date,
                        ),
                        # Сценарий 2: бронь начинается до check_out и заканчивается после
                        and_(
                            Booking.check_in_date < check_out_date,
                            Booking.check_out_date >= check_out_date,
                        ),
                        # Сценарий 3: бронь полностью внутри запрашиваемого периода
                        and_(
                            Booking.check_in_date >= check_in_date,
                            Booking.check_out_date <= check_out_date,
                        ),
                    ),
                )
            )
            .scalar_subquery()
        )

        # Основной запрос для поиска свободных комнат
        query = (
            select(Room)
            .where(
                and_(
                    Room.hotel_id == hotel_id,
                    Room.id.notin_(booked_rooms_subquery),
                    Room.max_guests >= guests,
                    Room.quantity > 0,
                )
            )
            .distinct()
        )

        result = await session.execute(query)
        return result.scalars().all()
