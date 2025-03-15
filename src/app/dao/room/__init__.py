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
                    Booking.check_out_date >= check_in_date,
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

    @classmethod
    async def get_room_availability(
        hotel_id: int,
        guest_count: int,
        check_in_date: date,
        check_out_date: date,
        session: AsyncSession,
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
        # Основной запрос для получения доступных номеров

        query = (
            select(
                RoomType.name.label("room_type"),
                Room.max_guests.label("max_guests"),
                RoomPrice.price.label("price_per_night"),
                Room.id.label("room_id"),
                Room.quantity.label("total_rooms"),
                func.count(Room.id).label("available_rooms"),
            )
            .join(Room.room_type_variant)
            .join(Room.room_prices)
            .where(
                and_(
                    Room.hotel_id == hotel_id,
                    Room.id.notin_(booked_rooms_subquery),
                    RoomPrice.guest_quantity == guest_count,
                )
            )
            .group_by(
                RoomType.name,
                Room.max_guests,
                RoomPrice.price,
                Room.id,
                Room.quantity,
            )
        )

        result = await session.execute(query)
        rows = result.fetchall()

        # Форматирование результата
        availability = []
        current_type = None
        current_room = None

        for row in rows:
            if row.room_type != current_type:
                current_type = row.room_type
                availability.append({"room_type": row.room_type, "variants": []})

            variant_data = {
                "max_guests": row.max_guests,
                "price_per_night": float(row.price_per_night),
                "available_rooms": row.available_rooms,
                "total_rooms": row.total_rooms,
                "features": [],  # Здесь можно добавить параметры номера
            }

            availability[-1]["variants"].append(variant_data)

        return availability
