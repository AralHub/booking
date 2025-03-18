from datetime import date
from sqlalchemy import and_, func, or_, select, case, text, literal_column, table
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
        guests: list[int],
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

        # Calculate stay duration for price calculation
        stay_duration = (check_out_date - check_in_date).days

        # First, get available rooms
        available_rooms = (
            select(Room)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(
                and_(
                    Room.hotel_id == hotel_id,
                    Room.id.notin_(booked_rooms_subquery),
                    Room.max_guests >= max(guests),
                    Room.quantity > 0,
                )
            )
        )

        result = await session.execute(available_rooms)
        rooms = result.scalars().all()

        # Format the results with different occupancy options
        formatted_rooms = []
        for room in rooms:
            room_type_query = select(RoomType).where(RoomType.id == room.room_type_id)
            room_type_result = await session.execute(room_type_query)
            room_type = room_type_result.scalar_one()

            pricing_options = []
            for occupancy in range(1, room.max_guests + 1):
                price_query = select(RoomPrice).where(
                    and_(
                        RoomPrice.room_id == room.id,
                        RoomPrice.guest_quantity == occupancy,
                    )
                )
                price_result = await session.execute(price_query)
                price_record = price_result.scalar()

                daily_price = price_record.price if price_record else room.base_price
                total_price = daily_price * stay_duration

                pricing_options.append(
                    {
                        "occupancy": occupancy,
                        "daily_price": daily_price,
                        "total_price": total_price,
                    }
                )

            formatted_rooms.append(
                {
                    "room_id": room.id,
                    "hotel_id": room.hotel_id,
                    "room_type_id": room.room_type_id,
                    "room_type_name": room_type.name,
                    "quantity": room.quantity,
                    "max_guests": room.max_guests,
                    "base_price": room.base_price,
                    "pricing_options": pricing_options,
                }
            )

        return formatted_rooms
