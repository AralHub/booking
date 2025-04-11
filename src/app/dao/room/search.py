import asyncio
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import Room
from app.models.room.types import RoomType

from app.dao.booking import BookingDAO
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO

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
            if booked_count >= room.quantity:
                continue  # Room is fully booked

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

            available_quantity = room.quantity - booked_count

            # Fetch the price for the room considering guest count
            price = await RoomPriceDAO.get_room_price(
                session=session,
                room_id=room.id,
            )

            room_data = {
                "id": room.id,
                "quantity": room.quantity,
                "available_quantity": available_quantity,
                "max_guests": room.max_guests,
                "room_type_id": room.room_type_id,
                "room_type_name": room_type_name,
                "base_price": room.base_price,
                "price_per_guest": price if price else None,
            }
            rooms_data.append(room_data)

        return rooms_data
