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
    async def get_available_rooms(
        cls,
        session: AsyncSession,
        hotel_id: int,
        check_in_date: date,
        check_out_date: date,
        guests: list[int],
    ):
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
        # First, get available rooms
        available_rooms = (
            select(Room)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(
                and_(
                    Room.hotel_id == hotel_id,
                    Room.id.notin_(booked_room_ids),
                )
            )
        )

        result = await session.execute(available_rooms)
        rooms = result.scalars().all()
        available_rooms = []
        total_days = (check_out_date - check_in_date).days
        for room in rooms:
            pricing_options = []
            print("=========================", room.use_dinamic_price)
            if room.use_dinamic_price:
                for occupancy in range(1, room.max_guests + 1):
                    room_price_for_occupancy = (
                        await RoomPriceDAO.get_room_price_by_guest_quantity(
                            session=session,
                            room_id=room.id,
                            guest_quantity=occupancy,
                        )
                    )
                    if room_price_for_occupancy:
                        total_price = room_price_for_occupancy * total_days

                        # Ensure we convert Decimal to float for JSON serialization
                        pricing_options.append(
                            {
                                "occupancy": occupancy,
                                "total_price": total_price,
                            }
                        )
            else:
                room_price = room.base_price
                total_price = room_price * total_days
                pricing_options.append(
                    {
                        "occupancy": room.max_guests,
                        "total_price": total_price,
                    }
                )
            available_rooms.append(
                {
                    "room_id": room.id,
                    "hotel_id": room.hotel_id,
                    "room_type_id": room.room_type_id,
                    "quantity": room.quantity,
                    "max_guests": room.max_guests,
                    "base_price": room.base_price,
                    "pricing_options": pricing_options,
                }
            )
        return available_rooms
