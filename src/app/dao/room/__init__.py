from datetime import date

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.booking import Booking


from app.models.room import Room, RoomPrice
from app.models.room.bed import BedType, RoomBedConfiguration
from app.models.room.types import RoomType


class RoomTypeDAO(BaseDAO):
    model = RoomType


class BedTypeDAO(BaseDAO):
    model = BedType


class RoomBedConfDAO(BaseDAO):
    model = RoomBedConfiguration


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def get_room_price(cls, session: AsyncSession, room_id: int):
        room = await cls.get_one_or_none_by_id(
            session=session,
            data_id=room_id,
        )
        return room.base_price if room else None

    @classmethod
    async def get_available_rooms(
        db: AsyncSession,
        hotel_id: int,
        check_in_date: date,
        check_out_date: date,
        guests: int,
    ):
        # Подзапрос для поиска занятых комнат на указанные даты
        booked_rooms_subquery = (
            select(Booking.room_id)
            .where(
                and_(
                    Booking.check_in_date <= check_out_date,
                    Booking.check_out_date>=check_in_date,
                )
            )
            .scalar_subquery()
        )

        # Основной запрос для поиска свободных комнат
        query = (
            select(Room)
            .join(Room.room_prices)
            .where(
                and_(
                    Room.hotel_id == hotel_id,
                    Room.id.notin_(booked_rooms_subquery),
                    Room.max_guests >= guests,
                    RoomPrice.guest_quantity == guests,
                    Room.quantity > 0,  # Если нужно учитывать количество номеров
                )
            )
            .distinct()
        )

        result = await db.execute(query)
        return result.scalars().all()
