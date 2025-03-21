from datetime import date
from sqlalchemy import func, select, and_, or_
from sqlalchemy.types import Integer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.http_exceptions import BadRequestException, NotFoundException
from app.dao import BaseDAO
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO
from app.dao.user import UserDAO
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User

from app.models.booking import Booking, BookingStatus
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingCreateMultipleRoomsInternal,
)


class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    async def create_booking(
        cls,
        session: AsyncSession,
        booking_data: BookingCreateMultipleRooms,
        user_id: int,
    ):
        # Validate dates
        if booking_data.check_in_date >= booking_data.check_out_date:
            raise BadRequestException("Check-out date must be after check-in date")

        # Check if user exists
        db_user = await UserDAO.get_one_or_none_by_id(
            session=session,
            data_id=user_id,
        )
        if not db_user:
            raise NotFoundException("User not found")

        # Calculate total days for the booking
        total_days = (booking_data.check_out_date - booking_data.check_in_date).days

        # Verify each room and calculate total price
        total_price = 0
        validated_rooms_info = []

        for room_info in booking_data.rooms_info:
            # Check if room exists
            db_room = await RoomDAO.get_one_or_none_by_id(
                session=session,
                data_id=room_info.room_id,
            )
            if not db_room:
                raise NotFoundException(f"Room with ID {room_info.room_id} not found")

            # Check if guest count is valid for this room
            if room_info.guest_quantity > db_room.max_guests:
                raise BadRequestException(
                    f"Room {room_info.room_id} can only accommodate {db_room.max_guests} guests"
                )

            # Check room availability for the requested dates
            overlapping_bookings = await RoomDAO.get_overlapping_bookings(
                session=session,
                check_in_date=booking_data.check_in_date,
                check_out_date=booking_data.check_out_date,
                hotel_id=db_room.hotel_id,
            )
            # Calculate price for this room
            if db_room.use_dinamic_price:
                room_price = await RoomPriceDAO.get_room_price_by_guest_quantity(
                    session=session,
                    room_id=room_info.room_id,
                    guest_quantity=room_info.guest_quantity,
                )
            else:
                room_price = db_room.base_price

            room_total_price = total_days * room_price
            total_price += room_total_price

            # Add validated room info with price
            validated_room = room_info.model_dump()
            validated_room["price"] = room_price
            validated_room["total_price"] = room_total_price
            validated_rooms_info.append(validated_room)

        # Create booking with all rooms
        return await cls.create(
            session=session,
            values=BookingCreateMultipleRoomsInternal(
                check_in_date=booking_data.check_in_date,
                check_out_date=booking_data.check_out_date,
                rooms_info=validated_rooms_info,
                total_days=total_days,
                total_price=total_price,
                user_id=user_id,
                special_requests=(
                    booking_data.special_requests
                    if hasattr(booking_data, "special_requests")
                    else None
                ),
            ),
        )
