from datetime import date

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.booking import Booking


from app.models.room import Room
from app.models.room.bed import BedType, RoomBedConfiguration
from app.models.room.types import RoomType


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
        cls,
        session: AsyncSession,
        check_in: date,
        check_out: date,
        room_id: int,
    ):
        booked_rooms = (
            select(Booking)
            .where(
                and_(
                    Booking.room_id == room_id,
                    or_(
                        and_(
                            Booking.check_in_date >= check_in,
                            Booking.check_out_date <= check_out,
                        ),
                        and_(
                            Booking.check_in_date <= check_in,
                            Booking.check_out_date > check_in,
                        ),
                    ),
                )
            )
            .cte("booked_rooms")
        )
        get_available_rooms_query = (
            select(
                Room,
                (Room.quantity - func.count(booked_rooms.c.room_id)).label(
                    "rooms_left"
                ),
            )
            .select_from(Room)
            .join(booked_rooms, booked_rooms.c.room_id == Room.id, isouter=True)
            .where(Room.id == room_id)
            .group_by(Room)
        )

        # Execute the query
        result = await session.execute(get_available_rooms_query)

        room_with_availability = result.scalar()
        return room_with_availability


class RoomTypeDAO(BaseDAO):
    model = RoomType


class BedTypeDAO(BaseDAO):
    model = BedType


class RoomBedConfDAO(BaseDAO):
    model = RoomBedConfiguration
