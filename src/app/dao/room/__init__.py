from datetime import date
from sqlalchemy import and_, func, or_, select, case, text, literal_column, table
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.booking import Booking, BookingStatus
from app.dao.room.price import RoomPriceDAO
from app.models.room import Room
from app.models.room.price import RoomPrice
from app.models.room.types import RoomType


class RoomTypeDAO(BaseDAO):
    model = RoomType


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def get_overlapping_bookings(
        cls,
        session: AsyncSession,
        check_in_date: date,
        check_out_date: date,
        hotel_id: int,
    ):
        overlapping_bookings_query = select(Booking).where(
            and_(
                # Check only active bookings (not cancelled)
                Booking.status != BookingStatus.CANCELLED,
                # Check all possible date overlaps
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

        overlapping_bookings = (
            (await session.execute(overlapping_bookings_query)).scalars().all()
        )
        return overlapping_bookings

    @classmethod
    def _can_accommodate_guests(cls, rooms, guest_groups):
        """
        Проверяет, можно ли разместить все группы гостей в доступных комнатах.

        Args:
            rooms: Список доступных комнат, отсортированных по вместимости
            guest_groups: Список групп гостей, отсортированных по убыванию

        Returns:
            bool: True, если все группы могут быть размещены
        """
        # Создаем копию списка комнат, чтобы не изменять оригинал
        available_rooms = [(room.id, room.max_guests) for room in rooms]

        # Пытаемся разместить каждую группу
        for group_size in guest_groups:
            placed = False

            # Ищем подходящую комнату (по принципу наилучшего соответствия)
            best_room_idx = None
            min_waste = float("inf")

            for i, (room_id, capacity) in enumerate(available_rooms):
                if capacity >= group_size:
                    waste = capacity - group_size
                    if waste < min_waste:
                        min_waste = waste
                        best_room_idx = i

            if best_room_idx is not None:
                # Размещаем группу в найденной комнате и удаляем её из доступных
                available_rooms.pop(best_room_idx)
                placed = True

            if not placed:
                return False  # Не можем разместить текущую группу

        return True  # Все группы размещены успешно

    @classmethod
    async def get_available_rooms(
        cls,
        session: AsyncSession,
        hotel_id: int,
        check_in_date: date,
        check_out_date: date,
        guests: list[int],
    ):
        print(f"Запрошенные группы гостей: {guests}")
        overlapping_bookings = await cls.get_overlapping_bookings(
            session=session,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_id=hotel_id,
        )

        # Extract all booked room IDs from the overlapping bookings
        booked_room_ids = []
        for booking in overlapping_bookings:
            for room_info in booking.rooms_info:
                booked_room_ids.append(room_info["room_id"])
        print("=========================", booked_room_ids)

        # Get all available rooms
        available_rooms_query = (
            select(Room)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(
                and_(
                    Room.hotel_id == hotel_id,
                    Room.id.notin_(booked_room_ids),
                )
            )
        )

        result = await session.execute(available_rooms_query)
        rooms = result.scalars().all()
        print(f"Всего доступных комнат: {len(rooms)}")

        # Сортируем гостей по убыванию (сначала размещаем большие группы)
        sorted_guests = sorted(guests, reverse=True)
        print(f"Отсортированные группы гостей: {sorted_guests}")

        # Сортируем комнаты по вместимости
        sorted_rooms = sorted(rooms, key=lambda r: r.max_guests)

        # Создаем список доступных комнат с учетом распределения гостей
        available_rooms_result = []
        total_days = (check_out_date - check_in_date).days

        # Проверяем возможность размещения всех групп
        can_accommodate_all = cls._can_accommodate_guests(sorted_rooms, sorted_guests)

        # Формируем результат только с подходящими для групп комнатами
        for room in rooms:
            # Находим группы, которые могут быть размещены в этой комнате
            suitable_groups = [g for g in guests if g <= room.max_guests]

            if not suitable_groups:
                continue  # Пропускаем комнаты, не подходящие ни для одной группы

            pricing_options = []
            print("=========================", room.use_dinamic_price)

            if room.use_dinamic_price:
                for occupancy in range(1, room.max_guests + 1):
                    # Показывать цены только для возможных размеров групп
                    if occupancy in suitable_groups:
                        room_price_for_occupancy = (
                            await RoomPriceDAO.get_room_price_by_guest_quantity(
                                session=session,
                                room_id=room.id,
                                guest_quantity=occupancy,
                            )
                        )
                        if room_price_for_occupancy:
                            total_price = room_price_for_occupancy * total_days

                            pricing_options.append(
                                {
                                    "occupancy": occupancy,
                                    "total_price": total_price,
                                    "suitable_for_groups": [
                                        g for g in guests if g == occupancy
                                    ],
                                }
                            )
            else:
                room_price = room.base_price
                total_price = room_price * total_days

                # Показываем только для подходящих групп
                suitable_max_groups = [g for g in guests if g <= room.max_guests]

                pricing_options.append(
                    {
                        "occupancy": room.max_guests,
                        "total_price": total_price,
                        "suitable_for_groups": suitable_max_groups,
                    }
                )

            available_rooms_result.append(
                {
                    "room_id": room.id,
                    "hotel_id": room.hotel_id,
                    "room_type_id": room.room_type_id,
                    "quantity": room.quantity,
                    "max_guests": room.max_guests,
                    "base_price": room.base_price,
                    "pricing_options": pricing_options,
                    "suitable_for_groups": suitable_groups,
                    "can_accommodate_all_groups": can_accommodate_all,
                }
            )

        return available_rooms_result
