import asyncio
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import Room
from app.models.room.types import RoomType
from app.dao.hotel.chessboard import ChessBoardDAO
from app.dao.booking import BookingDAO
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO
from app.dao.room.amenities import RoomAmenityDAO
from app.dao.room.images import RoomImageDAO
import logging

logger = logging.getLogger(__name__)


class RoomSearchDAO(RoomDAO):
    @classmethod
    async def find_rooms_for_booking(
        cls,
        session: AsyncSession,
        hotel_id: int,
        check_in_date: date,
        check_out_date: date,
        guests: list[int],
    ):
        booked_rooms_dict = await BookingDAO.get_booked_rooms_count_by_hotel_id(
            session=session,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_id=hotel_id,
        )
        logger.info(f"Booked rooms count for hotel {hotel_id}: {booked_rooms_dict}")
        chessboard_availability = await ChessBoardDAO.get_available_rooms_by_dates(
            session=session,
            hotel_id=hotel_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
        )
        logger.info(
            f"Chessboard availability for hotel {hotel_id}: {chessboard_availability}"
        )

        available_rooms_stmt = (
            select(
                Room,
                RoomType.name.label("room_type_name"),
            )
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(Room.hotel_id == hotel_id)
        )
        available_rooms_result = await session.execute(available_rooms_stmt)
        available_rooms = available_rooms_result.all()

        rooms_data = []
        for room, room_type_name in available_rooms:
            room_id = room.id
            booked_count = booked_rooms_dict.get(room_id, 0)

            # Проверяем ограничения шахматки на весь период
            room_availability = chessboard_availability.get(room_id, {})
            is_available_by_chessboard = True
            min_available_from_chessboard = room.quantity

            # Если есть данные шахматки для этой комнаты, проверяем все даты
            if room_availability:
                current_date = check_in_date
                while current_date < check_out_date:
                    if current_date in room_availability:
                        # Если на эту дату комнат меньше, чем требуется, комната недоступна
                        available_count = room_availability[current_date]
                        min_available_from_chessboard = min(
                            min_available_from_chessboard, available_count
                        )
                        if available_count <= booked_count:
                            is_available_by_chessboard = False
                            break
                    current_date += timedelta(days=1)

            # Если комната недоступна по шахматке или полностью забронирована
            if not is_available_by_chessboard or booked_count >= room.quantity:
                continue
            # Учитываем ограничения шахматки при расчете доступного количества
            available_quantity = min(
                room.quantity - booked_count, min_available_from_chessboard
            )
            # Check availability for each guest count in guests
            check_tasks = []
            for guest_count in guests:
                check_task = BookingDAO.is_room_available(
                    session=session,
                    room=room,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    guest_quantity=guest_count,
                )
                check_tasks.append(check_task)
            check_results = await asyncio.gather(*check_tasks)
            if not all(check_results):
                continue  # Room can't accommodate all guest counts

            # available_quantity = room.quantity - booked_count

            # Fetch the price for the room considering guest count
            price = await RoomPriceDAO.get_room_price(
                session=session,
                room_id=room.id,
            )
            room_amenities = await RoomAmenityDAO.get_room_amenities(
                session=session,
                room_id=room.id,
            )
            room_images = await RoomImageDAO.get_room_images(
                session=session,
                hotel_id=hotel_id,
                room_id=room.id,
            )
            room_data = {
                "id": room.id,
                "quantity": room.quantity,
                "use_dinamic_price": room.use_dinamic_price,
                "available_quantity": available_quantity,
                "max_guests": room.max_guests,
                "room_type_id": room.room_type_id,
                "room_type": room_type_name,
                "base_price": room.base_price,
                "amenities": (
                    room_amenities.get("room_amenity_categories")
                    if room_amenities.get("room_amenity_categories")
                    else []
                ),
                "images": room_images if room_images else [],
                "price_per_guest": price if price else None,
            }
            rooms_data.append(room_data)

        return rooms_data
